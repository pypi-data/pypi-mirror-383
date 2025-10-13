import argparse
from pathlib import Path

import numpy as np
from Bio.Data import CodonTable
from Bio.PDB.Structure import Structure
# from loguru import logger as log

from dv2s.global_vars import log
from dv2s.classes import Fasta, Fold
from dv2s.utils import get_mafft, get_dssp, run_cmd, test_file


def parse_arg():
    arg = argparse.ArgumentParser(description=main.__doc__)
    fasta = arg.add_argument_group('Sequence input')
    fasta.add_argument('-dna', required=True, help='DNA sequences in FASTA format')
    fasta.add_argument('-protein_aln', help='Aligned protein sequences in FASTA format')
    fasta.add_argument('-table_id', default=1, type=int,
                       help='Translate table ID, default 1 (standard table)')

    structure = arg.add_argument_group('Structure input')
    structure.add_argument('-mode', choices=('consensus', 'map', 'skip'),
                           default='consensus',
                           help=('Use generated consensus sequence to predict protein structure, '
                                 'or map alignment to the given protein structure'))
    structure.add_argument('-pdb', help='Protein structure in PDB format')
    structure.add_argument('-mmcif', help='Protein structure in mmCIF format')
    structure.add_argument('-predict',
                           choices=('auto', 'esm', 'esm-long', 'boltz-2', 'alphafold2'),
                           default='auto', help='Protein structure predict method')
    structure.add_argument('-nvidia_key', help='nvidia API key file')

    options = arg.add_argument_group('Options')
    options.add_argument('-mask_low_plddt', action='store_true',
                         help='Mask low pLDDT score amino acids in predicted protein structure')
    options.add_argument('-min_plddt', default=0.3, type=float,
                         help='Minimum pLDDT value')
    options.add_argument('-gene', help='Gene name')
    options.add_argument('-organism',
                         help='organism name with quotation (eg: "Oryza sativa")')
    options.add_argument('-n', '-n_thread', dest='n_thread',
                         default=-1, type=int,
                         help='Number of threads, -1 for number of CPU cores')

    arg.add_argument('-output', help='Output folder')
    return arg.parse_args()


def init_arg(arg):
    arg.dna = test_file(arg.dna)
    arg.input_type = 'dna'
    if arg.protein_aln is not None:
        arg.protein_aln = test_file(arg.protein_aln)
        arg.input_type = 'protein_aln'

    if arg.pdb:
        arg.pdb = test_file(arg.pdb)
        arg.protein_file = Path(arg.pdb).resolve()
        arg.protein_format = 'pdb'
    if arg.nvidia_key:
        arg.nvidia_key = test_file(arg.nvidia_key)
        arg.key = arg.nvidia_key.read_text().strip()
    else:
        log.warning('No nvidia API key file provided. Only use ESM server and Uniprot')
        arg.key = ''
    if arg.mmcif:
        arg.mmcif = test_file(arg.mmcif)
        arg.protein_file = Path(arg.mmcif).resolve()
        arg.protein_format = 'mmcif'
    if arg.pdb and arg.mmcif:
        log.warning('Both PDB and mmCIF are provided, ignore the PDB file')
    if not any([arg.pdb, arg.mmcif]) and arg.mode == 'map':
        if all([arg.gene, arg.organism]):
            log.info(f'Try to fetch protein structure from Uniprot: '
                     f'{arg.gene} {arg.organism}')
            arg.mmcif = arg.dna.with_suffix('.mmcif')
            # uniprot return mmcif
            arg.mmcif, format = Fold.uniprot(arg.gene, arg.organism, arg.mmcif)
            arg.protein_file = Path(arg.mmcif).resolve()
            arg.protein_format = 'mmcif'
            if format == '':
                log.error(f'Failed to get protein structure from Uniprot for '
                          f'{arg.organism} {arg.gene}')
                raise SystemExit(404)
        else:
            log.error('Protein structure must be provided for "map" mode')
            log.error('Or you can set gene and taxon names to let the program '
                      'fetch protein structure from Uniprot')
            raise SystemExit(-1)
    if any([arg.pdb, arg.mmcif]) and arg.mode == 'consensus':
        log.warning('Please make sure the input protein structure is predicted '
                    'from protein consensus sequence')
    if arg.output is None:
        arg.output = arg.dna.parent / f'{arg.dna.stem}-result'
    else:
        arg.output = Path(arg.output).resolve()
    if arg.output.exists():
        log.error(f'Output folder {arg.output} already exists')
        raise SystemExit(-1)
    else:
        arg.output.mkdir()
    return arg


def prepare_clean_aln(arg) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # translate and filter
    name_list, dna_list, aa_list = Fasta.translate(Fasta.parse_fasta(arg.dna),
                                                   arg.table_id)
    dna_filtered = arg.output / arg.dna.with_suffix('.dna.fasta').name
    protein_filtered = arg.output / arg.dna.with_suffix('.protein.fasta').name
    Fasta.write_fasta(zip(name_list, dna_list), dna_filtered)
    Fasta.write_fasta(zip(name_list, aa_list), protein_filtered)
    log.debug('MAFFT will automatically remove stop codon symbols in sequences')
    # align and map
    if arg.protein_aln is not None:
        log.info(f'Found aligned protein sequences in {arg.protein_aln}, skip alignment')
        protein_align = arg.protein_aln
    else:
        protein_align = align_seq(protein_filtered, arg.n_thread)
    protein_name, protein_seq = Fasta.aln_to_array(Fasta.parse_fasta(protein_align))

    if arg.mode == 'map':
        protein_ref_seq = Fold.get_seq(arg.protein_file, arg.protein_format)
        ref_protein_len = len(protein_ref_seq)
        protein_len = protein_seq.shape[1]
        if ref_protein_len != protein_len:
            log.error(f'Given protein structure sequence ({ref_protein_len} bp) '
                      f'should have same length with translated protein sequence'
                      f' ({protein_len:d} bp)')
            log.error(f'The result may be invalid')
            log.error(f'Please consider to use another protein structure '
                      f'input or use the "consensus" mode')
        ref_seq_file = arg.output / arg.protein_file.with_suffix('.protein_ref.seq').name
        Fasta.write_fasta([(arg.protein_file.stem, protein_ref_seq)],
                          ref_seq_file)
        protein_seq = map_align_to_ref(ref_seq_file, protein_align, arg.n_thread)


    dna_name, dna_seq_raw = Fasta.fasta_to_array(Fasta.parse_fasta(dna_filtered))
    dna_seq = Fasta.protein_aln_to_dna_aln(protein_seq, dna_seq_raw)
    dna_align = arg.output / arg.dna.with_suffix('.dna.aln').name
    Fasta.array_to_fasta(dna_name, dna_seq, dna_align)
    protein_seq_no_gap, _ = remove_gap(protein_seq, 'Protein')
    dna_seq_no_gap, _ = remove_gap(dna_seq, 'DNA')
    if protein_seq_no_gap.shape[1]*3 != dna_seq_no_gap.shape[1]:
        log.critical('Failed to map DNA and protein alignments')
        log.critical(f'Please check the homology of the input sequences')
        raise SystemExit(-1)
    # log.error([protein_seq.shape, dna_seq.shape, protein_seq_no_gap.shape, dna_seq_no_gap.shape])
    if arg.mode == 'map':
        # protein_seq_no_gap.shape[1] != ref_protein_len:
        fail_map = ref_protein_len - protein_seq_no_gap.shape[1]
        log.critical(f'Protein reference have {fail_map} sites that cannot be '
                     f'mapped to the alignment')
        raise SystemExit(-2)
    protein_seq_clean = Fasta.recheck(protein_seq_no_gap, 'protein')
    dna_seq_clean = Fasta.recheck(dna_seq_no_gap, 'DNA')
    protein_final = arg.output / arg.dna.with_suffix('.clean_protein.aln').name
    dna_final = arg.output / arg.dna.with_suffix('.clean_dna.aln').name
    Fasta.array_to_fasta(dna_name, dna_seq_clean, dna_final)
    Fasta.array_to_fasta(protein_name, protein_seq_clean, protein_final)

    # same names
    return dna_name, dna_seq_clean, protein_seq_clean


def align_seq(seq: Path, n_thread: int) -> Path|None:
    mafft_bin = get_mafft()
    log.info(f'Aligning {seq}')
    aln = seq.with_suffix('.aln')
    tmp_file = seq.with_suffix('.mafft.log')
    # globalpair for CDS alignment
    cmd = (f'{mafft_bin} --globalpair --maxiterate 1000 --thread {n_thread} '
           f'{seq} > {aln}')
    ok = run_cmd(cmd, tmp_file, 'MAFFT')
    if ok:
        log.info(f'{seq.name} -> {aln.name} finished')
        return aln
    else:
        log.error(f'Failed to run command: {cmd}')
        raise SystemExit(-10)


def remove_gap(align: np.ndarray, aln_name: str) -> tuple[np.ndarray, np.ndarray]:
    """
    In translation step, internal stop and non 3x sequence are already removed,
    so that we can assure that non-3x gaps is no need to worry.
    """
    no_gap_list = list()
    for i in range(align.shape[1]):
        col = align[:, i]
        col_count = np.unique_counts(col)
        # get_consensus by max occurrence
        letter = col_count.values[np.argmax(col_count.counts)]
        if letter != b'-':
            no_gap_list.append(i)
        else:
            continue
    if no_gap_list:
        log.info(f'Remove {len(no_gap_list)} gaps from {aln_name} alignment')
    no_gap_mask = np.array(no_gap_list)
    align_no_gap = align[:, no_gap_mask]
    return align_no_gap, no_gap_mask


def normalized_entropy(count: np.ndarray, n_row: int, max_h: float) -> float:
    """
    From OGU. Edit max_H
    Calculate normalized entropy.
    """
    count_ratio = count / n_row
    log2_p_j = np.log2(count_ratio)
    entropy = -1 * np.sum(log2_p_j * count_ratio) / max_h
    # entropy should > 0
    return max(0, entropy)


def nucleotide_diversity(count: np.ndarray) -> float:
    """
    From OGU.
    Get nucleotide diversity (pi) from one column
    """
    n_row  = np.sum(count)
    total_pairs = n_row * (n_row-1) / 2
    same_pairs = np.sum(count * (count - 1) / 2)
    sum_dij = total_pairs - same_pairs
    pi = sum_dij / total_pairs
    return max(0, pi)


def pi_omega(dna_array: np.ndarray, table_id: int) -> tuple[
    np.ndarray, np.ndarray, np.ndarray]:
    # pi_n / pi_s
    forward_table = CodonTable.generic_by_id[table_id].forward_table
    # https://pmc.ncbi.nlm.nih.gov/articles/PMC2734133
    # https://pmc.ncbi.nlm.nih.gov/articles/PMC4316684/
    n_row = dna_array.shape[0]
    total_pairs = n_row * (n_row - 1) / 2
    pi_n_list = list()
    pi_s_list = list()
    for i in range(0, dna_array.shape[1], 3):
        codon_base = dna_array[:, i:i+3]
        codon = np.array([b''.join(i) for i in codon_base])
        codon_count = np.unique_counts(codon)
        values = codon_count.values
        counts = codon_count.counts

        same_pairs = np.sum(counts*(counts-1)) / 2
        diff_pairs = total_pairs - same_pairs
        # synonymous
        s_pair = 0
        for j in range(len(values)-1):
            for k in range(j+1, len(values)):
                codon_str = values[j].decode('ascii')
                codon_str2 = values[k].decode('ascii')
                if (forward_table.get(codon_str, '-')
                        == forward_table.get(codon_str2, '-')):
                    s_pair += counts[j] * counts[k] / 2
        # nonsynonymous
        n_pair = diff_pairs - s_pair
        pi_n = n_pair / total_pairs
        pi_s = s_pair / total_pairs
        pi_n_list.append(pi_n)
        pi_s_list.append(pi_s)
    pi_n_array = np.array(pi_n_list)
    pi_s_array = np.array(pi_s_list)
    with np.errstate(divide='ignore', invalid='ignore'):
        pi_omega_array = pi_n_array / pi_s_array
    return pi_n_array, pi_s_array, pi_omega_array


def map_align_to_ref(ref: Path, aln: Path, n_thread: int) -> np.ndarray:
    # ref: protein pdb sequence
    # aln: protein align
    mafft_bin = get_mafft()
    log.info(f'Merge {aln} to reference {ref}')
    out_aln = aln.with_suffix('.merge.aln')
    tmp_file = ref.with_suffix('.merge.log')
    cmd = (f'{mafft_bin} --globalpair --maxiterate 1000 --keeplength '
           f'--thread {n_thread} --add {ref} {aln} > {out_aln}')
    ok = run_cmd(cmd, tmp_file, 'MAFFT')
    if not ok:
        log.error(f'Failed to run command: {cmd}')
        raise SystemExit(-10)
    names, seqs = Fasta.aln_to_array(Fasta.parse_fasta(out_aln))
    # last seq is reference
    # do not import ref seq to the alignment, only use the gap info
    gap_mask = (seqs[-1]==b'-')
    seqs[:, gap_mask] = b'-'
    log.warning(f'Remove {np.sum(~gap_mask)} gaps from alignment')
    # todo: keep site that ref is aa but consensus is gap?
    # keep_gap_mask = np.bitwise_and(seqs[-1, :]!=b'-' , seqs[0, :]==b'-')
    merged_aln = seqs[:-1, :]
    Fasta.array_to_fasta(names, merged_aln, out_aln)
    return merged_aln


def analyze_aln(seq_array: np.ndarray, seq_type='dna') -> tuple:
    # keep stop symbol?
    if seq_type == 'dna':
        n = 3
        # 64 codons without gap
        max_h = np.log2(64)
    else:
        n = 1
        # 20 amino acids without gap
        max_h = np.log2(20)
    c_seq = list()
    c_count = list()
    c_entropy = list()
    c_pi = list()
    no_gap_mask = list()
    # iter over col
    for i in range(0, seq_array.shape[1], n):
        col = seq_array[:, i:i+n]
        col = np.array([b''.join(i) for i in col])
        col_count = np.unique_counts(col)
        # get_consensus by max occurrence
        count = np.max(col_count.counts)
        letter = col_count.values[np.argmax(col_count.counts)]
        c_seq.append(letter)
        c_count.append(count)
        c_entropy.append(normalized_entropy(col_count.counts,seq_array.shape[0], max_h))
        c_pi.append(nucleotide_diversity(col_count.counts))
    c_count_ratio = np.array(c_count) / seq_array.shape[0]
    return (seq_array, np.array(c_seq), c_count_ratio,
            np.array(c_entropy), np.array(c_pi))


def get_structure(seq: str, arg) -> Structure:
    # linked with main logic, do not place into Fold
    if arg.mode == 'skip':
        log.info(f'Skip protein structure predict and analyze due to "-mode skip')
        log.info('Done')
        raise SystemExit(0)
    if arg.mode == 'map' or (arg.mode == 'consensus' and hasattr(arg, 'protein_file')):
        return Fold.read(arg.protein_file, arg.protein_format)
    arg.protein_file = arg.dna.with_suffix(f'.predict.structure')
    # stable -> good -> slow
    name_methods = {'esm': Fold.esmfold, 'esm-long': Fold.esmfold_nvidia,
                    'boltz-2': Fold.boltz2_nvidia, 'alphafold2': Fold.alphafold2_nvidia}
    if arg.predict == 'auto':
        methods = (Fold.esmfold, Fold.esmfold_nvidia, Fold.boltz2_nvidia,
                   Fold.alphafold2_nvidia)
    else:
        methods = (name_methods[arg.predict],)
    format = ''
    for method in methods:
        predicted, format = method(seq, arg.protein_file, arg.key)
        arg.protein_format = format
        if format:
            break
    if format == '':
        log.error(f'Failed to predict protein structure automatically')
        log.error(f'Please use other methods/servers '
                  f'(AlphaFold, Boltz, ESM, NVIDIA NIM) to '
                  f'predict {arg.protein_cons_out} and use "-mmcif/-pdb filename" '
                  f'to rerun')
        raise SystemExit(400)
    new_name = arg.output / arg.protein_file.with_suffix(f'.{arg.protein_format}').name
    if new_name.exists():
        log.warning(f'Overwriting {new_name}')
        new_name.unlink()
    arg.protein_file.rename(new_name)
    arg.protein_file = new_name
    return Fold.read(arg.protein_file, arg.protein_format)


def output_table(head, d_cons_seq, d_cons_count, p_cons_seq, plddt, d_entropy,
                 d_pi, d_pi_omega, p_entropy, p_pi,
                 sasa, rasa, second_stru, output):
    index = np.arange(1, p_cons_seq.shape[0] + 1)
    data = np.column_stack((index, d_cons_seq.astype(str), d_cons_count.round(6),
                            p_cons_seq.astype(str), plddt.round(6),
                            d_entropy.round(6), d_pi.round(6), d_pi_omega.round(6), p_entropy.round(6), p_pi.round(6),
                            sasa.round(6), rasa.round(6), second_stru))
    out_data = np.vstack((head, data))
    np.savetxt(output, out_data, fmt='%s', delimiter=',')
    return output


def split_align_by_2nd_structure(name: np.ndarray, align: np.ndarray,
                                 secondary_structure: np.ndarray,
                                 align_type: str,
                                 output: Path) -> tuple[Path, Path, Path]:
    # since OV/tiger and other software can alreadly split align by variance value
    # only split by 2nd/3rd protein structure
    # from https://biopython.org/docs/latest/api/Bio.PDB.DSSP.html
    helix_letter = list('HGI')
    strand_letter = list('EB')
    coil_letter = list('TS')
    undefined_letter = list('-')
    # index
    helix_i = np.where(np.isin(secondary_structure, helix_letter, ))[0]
    strand_i = np.where(np.isin(secondary_structure, strand_letter))[0]
    coil_i = np.where(np.isin(secondary_structure, coil_letter))[0]
    undefined_i = np.where(np.isin(secondary_structure, undefined_letter))[0]
    if align_type == 'DNA':
        helix_i = (helix_i.reshape(-1, 1)+np.arange(3)).flatten()
        strand_i = (strand_i.reshape(-1, 1)+np.arange(3)).flatten()
        coil_i = (coil_i.reshape(-1, 1)+np.arange(3)).flatten()
        undefined_i = (undefined_i.reshape(-1, 1)+np.arange(3)).flatten()
    helix = align[:, helix_i]
    strand = align[:, strand_i]
    coil = align[:, coil_i]
    undefined = align[:, undefined_i]
    log.info(f'In {align_type} alignment:')
    log.info(f'{helix.shape[1]} helix|{strand.shape[1]} strand|'
             f'{coil.shape[1]} coil|{undefined.shape[1]} undefined sites')
    helix_out = output.with_suffix(f'.helix_{align_type}.aln')
    strand_out = output.with_suffix(f'.strand_{align_type}.aln')
    coil_out = output.with_suffix(f'.coil_{align_type}.aln')
    Fasta.array_to_fasta(name, helix, helix_out)
    Fasta.array_to_fasta(name, strand, strand_out)
    Fasta.array_to_fasta(name, coil, coil_out)
    # print(align.shape)
    # print(secondary_structure.shape)
    # print(helix.shape)
    # print(strand.shape)
    # print(coil.shape)
    return helix_out, strand_out, coil_out


def rmsd():
    # todo: use mdtraj?
    pass


def main():
    """
    Visualize CDS evolution rate on dvm 3D structure.
    Ignore RNA editing on sequences or user should provide the modified version
    of input.
    """
    # init
    arg = parse_arg()
    arg = init_arg(arg)
    arg.log = arg.output / (arg.dna.stem+'.log')
    fmt = ('<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
           '<level>{level: <8}</level> | '
           '<cyan>{name}</cyan>:'
           '<cyan>{function}</cyan>:'
           '<cyan>{line}</cyan> - '
           '<level>{message}</level>')
    log.add(arg.log, format=fmt, level='DEBUG', backtrace=True, enqueue=True)
    log.debug(f'Input settings: {vars(arg)}')
    log.info(f'Input file: {arg.dna}')
    # prepare
    name_array, dna_array, protein_array = prepare_clean_aln(arg)
    # analyze seq
    (dna_array_no_gap, d_cons_seq, d_cons_ratio,
     d_entropy, d_pi) = analyze_aln(dna_array, seq_type='dna')
    d_pi_n, d_pi_s, d_pi_omega = pi_omega(dna_array_no_gap, arg.table_id)
    arg.dna_cons_out = arg.output / arg.dna.with_suffix('.dna_cons.fasta').name
    Fasta.array_to_fasta(np.array(['DNA consensus sequence']),
                         np.array([d_cons_seq]),
                         arg.dna_cons_out)
    (protein_array_no_gap, p_cons_seq, p_cons_ratio,
     p_entropy, p_pi) = analyze_aln(protein_array, seq_type='dvm')
    arg.protein_cons_out = arg.output / arg.dna.with_suffix('.protein_cons.fasta').name
    Fasta.array_to_fasta(np.array(['Protein consensus sequence']),
                         np.array([p_cons_seq]),
                         arg.protein_cons_out)
    # analyze structure
    p_cons_seq_str = b''.join(p_cons_seq).decode('utf-8')
    # terminate if arg.mode is "skip"
    structure = get_structure(p_cons_seq_str, arg)
    plddt = Fold.get_plddt(structure)
    sasa = Fold.get_sasa(structure)
    secondary_structure, rasa = Fold.run_dssp(structure, arg.protein_file, get_dssp())
    head_str = ('Index,DNA consensus,Consensus ratio,Protein sequence,'
                'pLDDT or B-factor,DNA entropy,DNA Pi,DNA Pi omega,'
                'Protein entropy,Protein Pi,' 'Protein SASA,Protein RASA,'
                'Protein secondary structure')
    head_array = np.array(head_str.split(','))
    out_csv = arg.output / arg.dna.with_suffix('.csv').name
    # output split align
    split_align_by_2nd_structure(name_array, dna_array, secondary_structure, 'DNA', out_csv)
    split_align_by_2nd_structure(name_array, protein_array, secondary_structure, 'protein', out_csv)
    # output table
    table_file = output_table(head_array, d_cons_seq, d_cons_ratio, p_cons_seq,
                              plddt, d_entropy, d_pi, d_pi_omega, p_entropy, p_pi,
                              sasa, rasa, secondary_structure,
                              out_csv)
    for col_name, data in zip(head_array[[2, 5, 6, 7, 8, 9]],
                              (d_cons_ratio, d_entropy, d_pi_s, d_pi_omega,
                               p_entropy, p_pi)):
        output_file = arg.output / arg.dna.with_suffix(f'.{col_name.replace(" ", "_")}.mmcif').name
        Fold.write_with_info(structure, data, output_file,
                             plddt, arg.mask_low_plddt, arg.min_plddt,
                             'mmcif')
    log.info(f'Output folder: {arg.output}')
    log.info(f'Output protein structure files: {arg.output}/*.mmcif')
    log.info(f'Output table: {table_file}')
    log.debug('See secondary structure explanation on '
              'https://biopython.org/docs/latest/api/Bio.PDB.DSSP.html')
    log.info('Done.')
    return


if __name__ == '__main__':
    main()
