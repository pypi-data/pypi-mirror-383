from typing import Iterable
from pathlib import Path
from os import chdir
from contextlib import redirect_stdout, redirect_stderr

import numpy as np
import requests
from Bio import SeqIO
from Bio.Data import CodonTable
from Bio.PDB import MMCIFParser, PDBParser, MMCIFIO, PDBIO
from Bio.PDB import SASA
from Bio.PDB.DSSP import DSSP
from Bio.PDB.Structure import Structure
from Bio.Seq import Seq
from Bio.SeqUtils import seq1

from dv2s.global_vars import log


class Fasta(object):
    @staticmethod
    def parse_fasta(fasta_file: Path) -> Iterable[tuple[str, str]]:
        """
        Import from treebarcode.
        Upper letter
        Return tuple(title: str, sequence: str)
        """
        with open(fasta_file, 'r') as f:
            record = []
            title = ''
            for line_raw in f:
                line = line_raw.strip()
                if line.startswith('>'):
                    if len(record) != 0:
                        join_str = ''.join(record)
                        if len(join_str.strip()) != 0:
                            yield title, join_str.upper()
                        else:
                            log.warning(f'Found empty sequence {title}')
                        record.clear()
                    title = line[1:]
                else:
                    record.append(line)
            if len(record) != 0:
                join_str = ''.join(record)
                if len(join_str.strip()) != 0:
                    yield title, join_str

    @staticmethod
    def write_fasta(records: Iterable[tuple[str, str]], filename: Path) -> Path:
        # sequence is in one line, no truncated
        if filename.exists():
            log.warning(f'Overwriting existing file {filename}')
        with open(filename, 'w') as f:
            for title, seq in records:
                f.write(f'>{title}\n')
                f.write(f'{seq}\n')
        return filename

    @staticmethod
    def fasta_to_array(records: Iterable[tuple[str, str]]) -> tuple[
        np.ndarray, np.ndarray]:
        records_ = list(records)
        name_array = np.array([i[0] for i in records_], dtype=np.str_)
        # S1 for 1 byte character, save more memory than 'U1' but
        # encode/decode is required
        seq_array = np.array([i[1] for i in records_], dtype=np.str_)
        return name_array, seq_array

    @staticmethod
    def aln_to_array(records: Iterable[tuple[str, str]]) -> tuple[
        np.ndarray, np.ndarray]:
        records_ = list(records)
        name_array = np.array([i[0] for i in records_], dtype=np.str_)
        # S1 for 1 byte character, save more memory than 'U1' but
        # encode/decode is required
        seq_array = np.array(
            [np.fromiter(i[1], dtype=np.dtype('S1')) for i in records_])
        return name_array, seq_array

    @staticmethod
    def array_to_fasta(name_array: np.ndarray, seq_array: np.ndarray,
                       output: Path) -> Path:
        # convert dtype='S1' to strings
        seq_list = list()
        for row in seq_array:
            seq_list.append(b''.join(row).decode('ascii'))
        return Fasta.write_fasta(zip(name_array, seq_list), output)

    @staticmethod
    def adjust_direction(dna: str, translate_table: CodonTable.CodonTable
                         ) ->  tuple[ bool, str, str]:
        """
        Adjust the direction of the sequence and do the translation.
        Considered internal stop.
        Ignore RNA editing.
        """
        # although OGU get sequence from gb considered strand, annotation errors is
        # existed
        seq = Seq(dna)
        new_seq = seq.reverse_complement()
        # if old seq has bad codon, reverse complemented seq is also bad, so that
        # omit second try-except
        try:
            old_aa = seq.translate(table=translate_table, stop_symbol='*')
        except CodonTable.TranslationError as e:
            log.warning(f'Translation error: {e}')
            return False, '', ''
        if old_aa.count('*') < 2:
            return False, dna, old_aa
        new_aa = new_seq.translate(table=translate_table, stop_symbol='*')
        if new_aa.count('*') < 2:
            return True, str(new_seq), new_aa
        # if too many '*', keep original
        return False, dna, old_aa

    @staticmethod
    def truncated_translate(dna: str, translate_table: CodonTable.CodonTable):
        # truncate sequence at first stop codon
        aa_list = list()
        forward_table = translate_table.forward_table
        for codon in range(0, len(dna), 3):
            aa = forward_table.get(dna[codon:codon+3], '-')
            aa_list.append(aa)
        aa_str = ''.join(aa_list)
        return aa_str

    @staticmethod
    def get_letters():
        # all tables share same letters
        table: CodonTable.CodonTable = CodonTable.standard_dna_table
        dna_letter = str(table.nucleotide_alphabet) + '-'
        protein_letter = str(table.protein_alphabet) + '-*'
        return dna_letter, protein_letter

    @staticmethod
    def recheck(align: np.ndarray, seq_type: str) -> np.ndarray:
        # protein sequences already used ambiguous bases, replace them in dna
        # is ok
        dna_letter, protein_letter = Fasta.get_letters()
        if seq_type == 'DNA':
            in_test = np.fromiter(dna_letter, dtype='S1')
        else:
            in_test = np.fromiter(protein_letter, dtype='S1')
        # Replace invalid letters with gaps. Assume they are in very little ratio
        new = align.copy()
        new[~np.isin(align, in_test)] = b'-'
        if seq_type == 'DNA':
            # todo: should we analyze stop codon?
            if new.shape[1] % 3 == 0:
                pass
                # log.info(f'Remove last stop codon in DNA sequences: '
                #          f'{align.shape[1]} -> {new.shape[1]}')
            else:
                last = abs(new.shape[1] // 3 * 3 - new.shape[1])
                new = new[:, :-last]
                log.warning(f'Truncate sequences due to translate error:'
                            f'from {align.shape[1]} -> {new.shape[1]}')
        return new

    @staticmethod
    def translate(record: Iterable[tuple[str, str]], table_id=1,
                  strict=True ) -> tuple[list[str], list[str], list[str]]:
        name_list = list()
        dna_list = list()
        aa_list = list()
        n_adjust = 0
        n_bad = 0
        translate_table = CodonTable.ambiguous_dna_by_id[table_id]
        for name, dna in record:
            # ensure all capitalized
            dna = dna.upper()
            length = len(dna)
            # start and stop codon at least 6 bases
            if length <= 6:
                n_bad += 1
                continue
            # length error
            elif length % 3 != 0 and strict:
                n_bad += 1
                continue
            if strict:
                adjusted, dna, aa = Fasta.adjust_direction(dna, translate_table)
            else:
                adjusted, dna, aa = Fasta.truncated_translate(dna, translate_table)
            # only consider internal stop and invalid codon, skip checking
            # start/stop codon given that input sequence may be truncated CDS
            if not aa:
                n_bad += 1
                continue
            if adjusted:
                n_adjust += 1
            name_list.append(name)
            dna_list.append(dna)
            aa_list.append(aa)
        if n_adjust:
            log.info(f'Adjusted direction of {n_adjust} sequences')
        if n_bad:
            log.info(f'Skip {n_bad} invalid records')
        log.info(f'Got {len(dna_list)} valid sequences')
        if not dna_list:
            log.error('No valid DNA sequences found')
            raise SystemExit(-1)
        return name_list, dna_list, aa_list

    @staticmethod
    def protein_aln_to_dna_aln(protein_align: np.ndarray, dna_seqs: np.ndarray
                               ) -> np.ndarray:
        dna_aln = np.full((protein_align.shape[0], protein_align.shape[1]*3),
                          b'-', dtype='S1')
        gap = np.array([b'-', b'-', b'-'], dtype='S1')
        for row_index in range(protein_align.shape[0]):
            dna_i = 0
            aln_i = 0
            for col_index in range(protein_align.shape[1]):
                if protein_align[row_index, col_index] != b'-':
                    codon = dna_seqs[row_index][dna_i:dna_i+3]
                    if not codon:
                        codon = gap
                    # array[0:3] = x cannot copy 3 letter but repeat one 3 times
                    dna_aln[row_index, aln_i:aln_i+1] = codon[0]
                    dna_aln[row_index, aln_i+1:aln_i+2] = codon[1]
                    dna_aln[row_index, aln_i+2:aln_i+3] = codon[2]
                    dna_i += 3
                aln_i += 3
        return dna_aln


class Fold(object):
    @staticmethod
    def read(filename, filetype):
        if filetype == 'pdb':
            parser = PDBParser()
        else:
            parser = MMCIFParser()
        structure = parser.get_structure('Input', filename)
        if len(list(structure.get_chains())) > 1:
            log.warning(f'More than one chain found in {filename}, '
                        f'only use the first')
        return structure

    @staticmethod
    def write(structure: Structure, output: Path, format='mmcif'):
        if format == 'mmcif':
            writer = MMCIFIO()
        else:
            writer = PDBIO()
        writer.set_structure(structure)
        # currently biopython.pdb does not support Path
        writer.save(str(output))
        return output

    @staticmethod
    def pdb2mmcif(pdb_file: Path, mmcif_file: Path):
        Fold.write(Fold.read(pdb_file, 'pdb'), mmcif_file)
        return mmcif_file

    @staticmethod
    def get_seq_from_invalid_pdb(structure_file: Path):
        last = 0
        seq = list()
        with open(structure_file, 'r') as _:
            for line in _:
                if line.startswith('ATOM'):
                    cols = line.split(' ')
                    cols = [i for i in cols if i]
                    aa = cols[3]
                    index = cols[5]
                    if index != last:
                        seq.append(seq1(aa))
                        last = index
        return ''.join(seq)

    @staticmethod
    def get_seq(structure_file: Path, file_type='pdb') -> str:
        seq_list = list()
        if file_type == 'mmcif':
            format = 'cif-seqres'
        else:
            format = 'pdb-seqres'
        for i in SeqIO.parse(structure_file, format):
            seq_list.append(i.seq)
        if not seq_list and file_type == 'pdb':
            return Fold.get_seq_from_invalid_pdb(structure_file)
        if len(seq_list) > 1:
            log.warning(
                f'More than one sequence found in {structure_file}, only use the first one')
        return str(seq_list[0])

    @staticmethod
    def get_plddt(structure) -> np.ndarray:
        b_factor = list()
        for residue in structure.get_residues():
            atoms = list(residue.get_atoms())
            avg_b = np.mean([i.get_bfactor() for i in atoms])
            b_factor.append(avg_b)
        b_factor_array = np.array(b_factor)
        if np.max(b_factor_array) > 1:
            # 0-1
            b_factor_array /= 100
        return b_factor_array

    @staticmethod
    def write_with_info(structure: Structure, data: np.ndarray, output: Path,
                        plddt: np.ndarray, mask_low_plddt: bool, min_plddt: float,
                        format='mmcif'):
        # for-loop and set_ methods edit value inplace
        n_inf = np.sum(np.isinf(data))
        if n_inf > 0:
            data[np.isinf(data)] = -np.inf
            inf_to_max = np.max(data) * 2
            log.warning(f'Replace {n_inf} Inf values with (max value*2) in {output}')
            data[np.isinf(data)] = inf_to_max
        n_nan = np.sum(np.isnan(data))
        if n_nan > 0:
            log.warning(f'Replace {n_nan} NaN values to 0 in {output}')
            data[np.isnan(data)] = 0
        _min = np.min(data)
        _max = np.max(data)
        if _min == _max:
            data = np.full_like(data, 50)
        else:
            data = 100 * (data-_min) / (_max-_min)
        structure2 = structure.copy()
        if mask_low_plddt:
            low_score_residues = (plddt < min_plddt)
        else:
            low_score_residues = (plddt < -np.inf)
        n_low_score = np.sum(low_score_residues)
        if n_low_score > 0:
            log.info(f'Mask {n_low_score} low pLDDT score residues to 0 B-factor in {output}')
            # todo: 0 is ok?
            data[low_score_residues] = 0
        data = np.round(data, 2)
        for residue, value in zip(structure2.get_residues(), data):
            for atom in residue.get_atoms():
                # 0-1 -> 0-100
                atom.set_bfactor(value)
        Fold.write(structure2, output, format)
        return output

    @staticmethod
    def precheck(seq, server_name, max_len):
        if len(seq) > max_len:
            log.warning(f'{server_name} supports up to {max_len} characters')
            log.warning('Suggest to use ESMAtlas '
                        '(https://esmatlas.com/resources?action=fold) or AlphaFold3')
            return False
        else:
            log.info(f'Try to predict protein structure via {server_name}')
        return True

    @staticmethod
    def write_predict(content: str, output: Path|str, server_name: str):
        output = Path(output).resolve()
        if output.exists():
            log.warning(f'Overwriting {output}')
        output.write_text(content)
        log.info(f'Got predict result via {server_name} -> {output.stem}')
        return output


    @staticmethod
    def esmfold(seq: str, output: Path, key='') -> tuple[Path, str] :
        max_len = 400
        server_name = 'ESM server API'
        format = 'pdb'
        if not Fold.precheck(seq, server_name, max_len):
            return output, ''
        url = 'https://api.esmatlas.com/foldSequence/v1/pdb/'
        headers = {'Content-Type': 'text/plain'}
        # payload = {'data': seq}
        response = requests.post(url, data=seq, headers=headers)
        if response.ok:
            Fold.write_predict(response.text, output, server_name)
            return output, format
        else:
            return output, ''

    @staticmethod
    def esmfold_nvidia(seq: str, output: Path, key: str) -> tuple[Path, str]:
        max_len = 1024
        server_name = 'ESM nvidia server API'
        format = 'pdb'
        if not Fold.precheck(seq, server_name, max_len):
            return output, ''
        url = "https://health.api.nvidia.com/v1/biology/nvidia/esmfold"

        headers = {'Authorization': f'Bearer {key}',
                   'Accept': 'application/json'}
        payload = {'sequence': f'{seq}'}
        try:
            response = requests.post(url, headers=headers, json=payload)
        except requests.exceptions.ReadTimeout:
            return output ,''
        if response.ok:
            result = response.json()
            if 'pdbs' in result and len(result['pdbs']) > 0:
                Fold.write_predict(result['pdbs'][0], output, server_name)
                return output, format
        return output, ''

    @staticmethod
    def boltz2_nvidia(seq: str, output: Path, key: str) -> tuple[Path, str]:
        max_len = 4096
        server_name = 'Boltz-2 nvidia server API'
        manual_timeout = 120
        format = 'mmcif'
        if not Fold.precheck(seq, server_name, max_len):
            return output, ''
        url = 'https://health.api.nvidia.com/v1/biology/mit/boltz2/predict'
        # 300 from nvidia default example
        headers = {'Authorization': f'Bearer {key}',
                   'NVCF-POLL-SECONDS': f'{manual_timeout}',
                   'Content-Type': 'application/json'}
        payload = {'polymers': [{'id': 'A', 'molecule_type': 'protein',
                                 'sequence': seq,
                                 'msa': {'uniref90': {
                                     'a3m': {'alignment': f'>seq1\n{seq}',
                                             'format': 'a3m'}}}}],
                   'ligands': [],
                   'recycling_steps': 1,
                   'sampling_steps': 50,
                   'diffusion_samples': 3,
                   'step_scale': 1.2,
                   'without_potentials': True}
        try:
            response = requests.post(url, json=payload, headers=headers,
                                     timeout=manual_timeout)
        except requests.exceptions.ReadTimeout:
            return output, ''
        if response.ok:
            result = response.json()
            if result['structures']:
                data = result['structures'][0]
                structure = data['structure']
                format_ = data['format']
                assert format == format_
                Fold.write_predict(structure, output, server_name)
                return output, format
        return output, ''

    @staticmethod
    def alphafold2_nvidia(seq: str, output: Path, key: str) -> tuple[Path, str]:
        max_len = 4096
        server_name = 'AlphaFold2 nvidia server API'
        format = 'pdb'
        if not Fold.precheck(seq, server_name, max_len):
            return output, ''
        url = 'https://health.api.nvidia.com/v1/biology/deepmind/alphafold2'
        headers = {'content-type': 'application/json',
                   'Authorization': f'Bearer {key}'}
        data = {'sequence': seq, 'algorithm': 'mmseqs2', 'e_value': 0.0001,
                'iterations': 1, 'databases': ['small_bfd'],
                'relax_prediction': False,
                'skip_template_search': True }
        timeout = 120
        try:
            response = requests.post(url, headers=headers, json=data,
                                     timeout=timeout)
        except requests.exceptions.Timeout:
            return output, ''
        if response.ok:
            result = response.json()
            if 'pdbs' in result and len(result['pdbs']) > 0:
                Fold.write_predict(result['pdbs'][0], output, server_name)
                return output, format
        return output, ''

    @staticmethod
    def uniprot_pdb(accession: str, output: Path) -> tuple[Path | None, str]:
        # uniport accession, not NCBI's
        url = 'https://alphafold.ebi.ac.uk/api/prediction/' + accession
        server_name = 'AlphaFold DB'
        # uniprot public key
        params = dict(key='AIzaSyCeurAJz7ZGjPQUtEaerUkBZ3TaBkXrY94')
        headers = {'accept': 'application/json'}
        response = requests.get(url, params=params, headers=headers)
        if response.ok:
            result = response.json()
            if len(result) != 0:
                # tool = result[0]['toolUsed']
                sequence = result[0]['sequence']
                cif_url = result[0]['cifUrl']
                response2 = requests.get(cif_url)
                if response2.ok:
                    Fold.write_predict(response2.text, output, server_name)
                    return output, sequence
        return None, ''

    @staticmethod
    def uniprot(gene: str, organism: str, output: Path) -> tuple[Path, str]:
        # https://www.uniprot.org/help/query-fields
        # https://www.uniprot.org/help/return_fields
        url = 'https://rest.uniprot.org/uniprotkb/search'
        params = dict(query=f'gene:{gene}+AND+organism_name:"{organism}"',
                      format='json', size=1,
                      fields='accession,gene_names,organism_name,xref_pdb')
        format = 'mmcif'
        # uniport does not accept quoted string in "query="
        req = requests.Request('GET', url, params=params)
        prepared = req.prepare()
        prepared.url = prepared.url.replace('%3A', ':').replace(
            '%2B', '&').replace('%2C', ',')
        response = requests.session().send(prepared)
        if response.ok:
            results = response.json()
            if results['results']:
                accession = results['results'][0]['primaryAccession']
                organism_name = results['results'][0]['organism'][
                    'scientificName']
                if organism_name.lower() != organism.lower():
                    log.error(f'Uniprot search result does not match organism name')
                    log.error(f'{accession=}\t{organism_name} != {organism}')
                    log.error(f'Please consider to use the "consensus" mode or '
                              f'input a valid pdb/mmcif file')
                    raise SystemExit(500)
                gene_ = results['results'][0]['genes'][0]['geneName']['value']
                if gene_.lower() == gene.lower():
                    log.info(f'Found uniprot record: {accession}, '
                             f'{organism_name}, {gene_}')
                    mmcif, seq = Fold.uniprot_pdb(accession, output)
                    if mmcif:
                        return mmcif, format
        return output, format

    @staticmethod
    def get_sasa(structure: Structure) -> np.ndarray:
        # 0-100+
        # solvent accessible surface areas
        sr = SASA.ShrakeRupley()
        # residue level
        sr.compute(structure, level='R')
        sasa_list = list()
        for r in structure.get_residues():
            sasa_list.append(r.sasa)
        return np.array(sasa_list)

    @staticmethod
    def run_dssp(structure: Structure, input_path: Path, dssp_path: str):
        # return secondary structure and relative accessible surface area
        # dssp use model as input, not strucutre
        # ignore other models
        dssp_path_p = Path(dssp_path).resolve()
        model = next(structure.get_models())
        cwd = Path.cwd()
        chdir(dssp_path_p.parent)
        with open(input_path.with_suffix('.dssp.log'), 'w') as f:
            with redirect_stdout(f), redirect_stderr(f):
                result = DSSP(model, str(input_path.resolve()), dssp=dssp_path)
        chdir(cwd)
        result_array = np.array(list(result))
        secondary_structure = result_array[:, 2]
        rasa = result_array[:, 3].astype(float)
        return secondary_structure, rasa
