import gradio as gr
from pathlib import Path
import argparse
import tempfile
import os


def create_gradio_interface():
    """Create Gradio interface to replace command line arguments"""

    css = """
    .header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .github-link {
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        margin: 10px 0;
        display: inline-block;
    }
    .github-link:hover {
        text-decoration: underline;
    }
    .output-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .tab-content {
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin-top: 10px;
    }
    .info-text {
        font-size: 12px;
        color: #666;
        margin-top: 5px;
    }
    """

    with gr.Blocks(title="CDS Evolution Rate Visualization Tool", css=css) as demo:
        # Header with cover image and GitHub link
        gr.HTML("""
        <div class="header">
            <h1>CDS Evolution Rate Visualization</h1>
            <p>Visualize CDS evolution rate distribution on protein 3D structure</p>
            <a href="https://github.com/wpwupingwp/protein" target="_blank" class="github-link">
                <i class="fab fa-github"></i> https://github.com/wpwupingwp/protein
            </a>
            <img src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=200&fit=crop" 
                 alt="Protein Structure" style="width: 400px; height: 200px; border-radius: 10px; margin-top: 15px;">
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                # Sequence input section
                gr.Markdown("### Sequence Input")
                dna_input = gr.File(label="DNA Sequence File (FASTA format)", file_types=[".fasta", ".fa"])
                table_id = gr.Number(label="Translation Table ID", value=1, precision=0)

                # Structure input section
                gr.Markdown("### Structure Input")
                mode = gr.Radio(choices=["consensus", "map"],
                                value="consensus",
                                label="Mode Selection")

                # 使用Row将两个文件上传组件放在同一行
                with gr.Row():
                    with gr.Column(scale=1):
                        pdb_file = gr.File(label="PDB Structure File", file_types=[".pdb"])
                    with gr.Column(scale=1):
                        mmcif_file = gr.File(label="mmCIF Structure File", file_types=[".cif"])

            with gr.Column(scale=1):
                # Options section
                gr.Markdown("### Options")
                predict_method = gr.Dropdown(
                    choices=["auto", "esm", "esm-long", "boltz-2", "alphafold2"],
                    value="auto",
                    label="Protein Structure Prediction Method"
                )
                mask_low_plddt = gr.Checkbox(label="Mask low pLDDT score amino acids")
                min_plddt = gr.Slider(minimum=0, maximum=1, value=0.3, step=0.01,
                                      label="Minimum pLDDT Value")

                # Gene Name、Organism Name与Number of Threads放在同一行
                with gr.Row():
                    gene_name = gr.Textbox(label="Gene Name")
                    organism_name = gr.Textbox(label="Organism Name")
                    n_threads = gr.Number(label="Number of Threads (-1=CPU cores)", value=-1, precision=0)

                # NVIDIA API Key section with tabs
                gr.Markdown("### NVIDIA API Key")
                with gr.Tabs():
                    with gr.TabItem("Text Input"):
                        nvidia_key_text = gr.Textbox(
                            label="Enter API Key",
                            type="password",
                            placeholder="Enter your NVIDIA API key here..."
                        )
                        gr.HTML('<div class="info-text">Your API key will be securely processed</div>')

                    with gr.TabItem("File Upload"):
                        nvidia_key_file = gr.File(
                            label="Upload API Key File",
                            file_types=[".txt"]
                        )
                        gr.HTML('<div class="info-text">Upload a text file containing your API key</div>')

                # Output section
                gr.Markdown("### Output Settings")
                output_dir = gr.Textbox(label="Output Directory", value="")

        # Submit button
        with gr.Row():
            submit_btn = gr.Button("Start Analysis", variant="primary", size="lg")

        # Output area
        with gr.Column():
            gr.Markdown("### Processing Log")
            output_text = gr.Textbox(label="", lines=8, interactive=False)

            # Results section
            with gr.Accordion("Analysis Results", open=False) as results_accordion:
                gr.Markdown("### Download Results")
                with gr.Row():
                    csv_output = gr.File(label="CSV Results")
                    mmcif_output = gr.File(label="mmCIF Structure Files")
                    cons_dna_output = gr.File(label="DNA Consensus")
                    cons_protein_output = gr.File(label="Protein Consensus")

        def process_inputs(dna_file, table_id_val, mode_val, pdb_file, mmcif_file,
                           predict_val, mask_low, min_plddt_val, gene, organism,
                           n_thread_val, nvidia_key_text, nvidia_key_file, output_dir_val):
            """Process input parameters and simulate analysis"""

            # Get API key from either text input or file
            api_key = None
            if nvidia_key_text and nvidia_key_text.strip():
                api_key = nvidia_key_text.strip()
            elif nvidia_key_file:
                try:
                    with open(nvidia_key_file.name, 'r') as f:
                        api_key = f.read().strip()
                except:
                    return "Error: Failed to read API key from file", None, None, None, None

            # Simulate parse_arg returned object
            class Args:
                def __init__(self):
                    pass

            args = Args()

            # Set parameters
            args.dna = Path(dna_file.name) if dna_file else None
            args.table_id = int(table_id_val)
            args.mode = mode_val
            args.pdb = Path(pdb_file.name) if pdb_file else None
            args.mmcif = Path(mmcif_file.name) if mmcif_file else None
            args.predict = predict_val
            args.mask_low_plddt = mask_low
            args.min_plddt = min_plddt_val
            args.gene = gene
            args.organism = organism
            args.n_thread = int(n_thread_val)
            args.nvidia_key = api_key
            args.output = Path(output_dir_val) if output_dir_val else None

            # Validate required parameters
            if not args.dna:
                return "Error: DNA sequence file is required", None, None, None, None

            # Simulate processing steps
            log_messages = [
                "Parameters set successfully:",
                f"- DNA file: {args.dna}",
                f"- Translation table ID: {args.table_id}",
                f"- Mode: {args.mode}",
                f"- Prediction method: {args.predict}",
                f"- API key provided: {'Yes' if api_key else 'No'}",
                "",
                "Starting analysis...",
                "Step 1: Reading DNA sequences... ✓",
                "Step 2: Translating to protein sequences... ✓",
                "Step 3: Multiple sequence alignment... ✓",
                "Step 4: Calculating evolutionary rates... ✓",
                "Step 5: Generating consensus sequences... ✓",
                "Step 6: Mapping to protein structure... ✓",
                "Step 7: Writing output files... ✓",
                "",
                "Analysis completed successfully!"
            ]

            # Create temporary output files for demonstration
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create sample output files
                csv_file = temp_path / "results.csv"
                csv_file.write_text(
                    "Index,DNA_consensus,Consensus_ratio,Protein_sequence,pLDDT,DNA_entropy,DNA_Pi,DNA_Pi_omega,Protein_entropy,Protein_Pi,Protein_SASA,Protein_RASA,Secondary_structure\n1,ATG,1.0,M,0.95,0.1,0.05,0.2,0.15,0.08,150.5,0.75,H")

                mmcif_file1 = temp_path / "dna_entropy.mmcif"
                mmcif_file1.write_text("Sample mmCIF structure file with DNA entropy data")

                mmcif_file2 = temp_path / "protein_pi.mmcif"
                mmcif_file2.write_text("Sample mmCIF structure file with protein Pi data")

                dna_cons_file = temp_path / "dna_consensus.fasta"
                dna_cons_file.write_text(">DNA_consensus_sequence\nATGGCCGAT...")

                protein_cons_file = temp_path / "protein_consensus.fasta"
                protein_cons_file.write_text(">Protein_consensus_sequence\nMAD...")

                # Prepare files for download
                output_files = [
                    str(csv_file),
                    [str(mmcif_file1), str(mmcif_file2)],
                    str(dna_cons_file),
                    str(protein_cons_file)
                ]

            return "\n".join(log_messages), output_files[0], output_files[1], output_files[2], output_files[3]

        # Connect event handling
        submit_btn.click(
            fn=process_inputs,
            inputs=[dna_input, table_id, mode, pdb_file, mmcif_file,
                    predict_method, mask_low_plddt, min_plddt, gene_name,
                    organism_name, n_threads, nvidia_key_text, nvidia_key_file, output_dir],
            outputs=[output_text, csv_output, mmcif_output, cons_dna_output, cons_protein_output]
        )

    return demo


# Create and launch interface
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(share=True)
