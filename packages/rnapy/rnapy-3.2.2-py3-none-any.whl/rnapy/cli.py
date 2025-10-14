#!/usr/bin/env python3
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Union, List, Any


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=level
    )


def parse_sequence_input(seq: Optional[str], fasta: Optional[str]) -> Union[str, List[str]]:
    """Parse sequence input from command line arguments"""
    if seq and fasta:
        raise ValueError("Cannot specify both --seq and --fasta")
    if not seq and not fasta:
        raise ValueError("Must specify either --seq or --fasta")
    
    if seq:
        # Handle comma-separated sequences
        if ',' in seq:
            return [s.strip() for s in seq.split(',')]
        return seq

    if fasta:
        # Return fasta file path, will be processed by toolkit
        return fasta
    # Should be unreachable due to checks above; keep for type checkers
    raise RuntimeError("Unreachable: invalid sequence input state")



def save_output(data: Any, save_dir: Optional[str], filename: str, format_type: str = "json") -> Optional[str]:
    """Save output data to file if save_dir is specified"""
    if not save_dir:
        return None

    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    if format_type == "json":
        output_file = save_path / f"{filename}.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return str(output_file)
    elif format_type == "npy":
        import numpy as np
        output_file = save_path / f"{filename}.npy"
        np.save(output_file, data)
        return str(output_file)

    return None


def print_summary(data: Any, command: str):
    """Print summary of results to terminal"""
    if command == "seq_embed":
        if isinstance(data, list):
            print(f"Extracted embeddings for {len(data)} sequences")
        else:
            print(f"Extracted embedding with shape: {data.shape}")
    elif command == "seq_compare":
        print(f"Sequence similarity: {data.get('sequence_similarity', 'N/A')}")
    elif command == "struct_predict":
        if isinstance(data, list):
            print(f"Predicted structures for {len(data)} sequences")
        else:
            if 'secondary_structure' in data:
                print(f"Secondary structure: {data['secondary_structure']}")
            elif 'structure_file' in data:
                print(f"3D structure saved to: {data['structure_file']}")
    elif command == "struct_compare":
        print(f"Structure similarity: {data.get('structure_similarity', 'N/A')}")
    elif command == "invfold_gen":
        print(f"Generated {len(data.get('sequences', []))} sequences")
        for i, seq in enumerate(data.get('sequences', [])):
            print(f"Sequence {i+1}: {seq[:50]}...")
    elif command == "msa_features":
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, 'shape'):
                    print(f"{key}: shape {value.shape}")
        else:
            print(f"MSA features shape: {data.shape}")
    elif command == "msa_analyze":
        print("MSA analysis completed:")
        for key, value in data.items():
            if key == 'consensus_sequence':
                print(f"Consensus: {value}")
            elif key == 'conservation_scores' and hasattr(value, 'mean'):
                print(f"Mean conservation: {value.mean():.3f}")
    elif command == "metric_lddt":
        print(f"LDDT score: {data.get('lddt', 'N/A')}")
    elif command == "metric_rmsd":
        print(f"RMSD: {data:.4f}" if isinstance(data, float) else str(data))
    elif command == "metric_tm_score":
        print(f"TM-score: {data.get('tm_score', 'N/A')}")


def _get_toolkit(config_dir: str = "configs", device: str = "cpu"):
    """Lazy import and initialize RNAToolkit"""
    try:
        from .toolkit import RNAToolkit
        from .core.config_loader import config_loader
        
        # Update config_dir if specified
        if config_dir != 'configs':
            config_loader.config_dir = Path(config_dir)
        
        return RNAToolkit(config_dir=config_dir, device=device), config_loader
    except ImportError as e:
        raise ImportError(f"Failed to import RNAToolkit. Missing dependencies: {e}")


def cmd_seq_embed(args):
    """Handle seq embed command"""
    sequences = parse_sequence_input(args.seq, args.fasta)
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)
    
    embeddings = toolkit.extract_embeddings(
        sequences=sequences,
        model=args.model,
        layer=args.layer,
        format=args.format,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"Embeddings saved to: {args.save_dir}")

    print_summary(embeddings, "seq_embed")

def cmd_seq_compare(args):
    """Handle seq compare command"""
    if args.seqs:
        sequences = [s.strip() for s in args.seqs.split(',')]
        if len(sequences) < 2:
            raise ValueError("At least two sequences are required for comparison")
        seq1, seq2 = sequences[0], sequences[1]
    elif args.seq1 and args.seq2:
        seq1, seq2 = args.seq1, args.seq2
    else:
        raise ValueError("Must specify either --seqs or --seq1 and --seq2")

    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    
    if hasattr(args, 'model') and args.model:
        toolkit.load_model(args.model, args.model_path)
        results = toolkit.compare_sequences(seq1=seq1, seq2=seq2, model=args.model)
    else:
        results = toolkit.compare_sequences(seq1=seq1, seq2=seq2)

    if args.save_dir:
        save_output(results, args.save_dir, "sequence_comparison")
        print(f"Sequence comparison results saved to: {args.save_dir}")

    print(f"Sequence 1: {seq1}")
    print(f"Sequence 2: {seq2}")
    print_summary(results, "seq_compare")


def cmd_seq_recovery(args):
    """Handle seq recovery command"""
    if not args.native or not args.designed:
        raise ValueError("Must specify both --native and --designed sequences")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    
    results = toolkit.calculate_sequence_recovery(args.native, args.designed)
    
    if args.save_dir:
        save_output(results, args.save_dir, "sequence_recovery")
        print(f"Sequence recovery results saved to: {args.save_dir}")
    
    print(f"Native sequence:   {args.native}")
    print(f"Designed sequence: {args.designed}")
    print(f"\nOverall Recovery: {results['overall_recovery']:.4f}")
    print(f"Total Matches: {results['total_matches']}/{results['total_positions']}")
    print("\nPer-Nucleotide Recovery:")
    for base in ['A', 'U', 'G', 'C']:
        rate = results['per_nucleotide_recovery'][base]
        count = results['nucleotide_counts'][base]
        print(f"  {base}: {rate:.4f} ({count} positions)")


def cmd_struct_predict(args):
    """Handle struct predict command"""
    sequences = parse_sequence_input(args.seq, args.fasta)

    # Infer structure type from model if not specified
    structure_type = args.structure_type
    if not structure_type:
        if args.model == "rhofold":
            structure_type = "3d"
        elif args.model in ["rna-fm", "mrna-fm", "rna_fm", "mrna_fm"]:
            structure_type = "2d"
        else:
            structure_type = "2d"  # Default

    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)

    results = toolkit.predict_structure(
        sequences=sequences,
        structure_type=structure_type,
        model=args.model,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"Structure prediction results saved to: {args.save_dir}")

    print_summary(results, "struct_predict")


def cmd_struct_compare(args):
    """Handle struct compare command"""
    if not args.struct1 or not args.struct2:
        raise ValueError("Must specify both --struct1 and --struct2")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    
    results = toolkit.compare_structures(args.struct1, args.struct2)
    
    if args.save_dir:
        save_output(results, args.save_dir, "structure_comparison")
        print(f"Structure comparison results saved to: {args.save_dir}")
    
    print(f"Structure 1: {args.struct1}")
    print(f"Structure 2: {args.struct2}")
    print_summary(results, "struct_compare")


def cmd_struct_f1(args):
    """Handle struct f1 command"""
    if not args.struct1 or not args.struct2:
        raise ValueError("Must specify both --struct1 and --struct2")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    
    results = toolkit.calculate_structure_f1(args.struct1, args.struct2)
    
    if args.save_dir:
        save_output(results, args.save_dir, "structure_f1")
        print(f"Structure F1 results saved to: {args.save_dir}")
    
    print(f"Structure 1: {args.struct1}")
    print(f"Structure 2: {args.struct2}")
    print(f"\nPrecision: {results['precision']:.4f}")
    print(f"Recall:    {results['recall']:.4f}")
    print(f"F1 Score:  {results['f1_score']:.4f}")


def cmd_invfold_gen(args):
    """Handle invfold gen command"""
    if not args.pdb:
        raise ValueError("Must specify --pdb for inverse folding")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)
    
    kwargs = {}
    if hasattr(args, 'ss_npy') and args.ss_npy:
        kwargs['secondary_structure_file'] = args.ss_npy
    if hasattr(args, 'n_samples') and args.n_samples:
        kwargs['n_samples'] = args.n_samples
    
    results = toolkit.generate_sequences_from_structure(
        structure_file=args.pdb,
        model=args.model,
        save_dir=args.save_dir,
        **kwargs
    )
    
    if args.save_dir:
        print(f"Generated sequences saved to: {args.save_dir}")
    
    print_summary(results, "invfold_gen")


def cmd_msa_features(args):
    """Handle msa features command"""
    sequences = parse_sequence_input(args.seq, args.fasta)

    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)

    features = toolkit.extract_msa_features(
        sequences=sequences,
        feature_type=args.feature_type,
        model=args.model,
        layer=args.layer,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"MSA features saved to: {args.save_dir}")

    print_summary(features, "msa_features")


def cmd_msa_analyze(args):
    """Handle msa analyze command"""
    sequences = parse_sequence_input(args.seq, args.fasta)
    
    # Convert single sequence or fasta file to list for MSA analysis
    if isinstance(sequences, str):
        if sequences.endswith(('.fasta', '.fa', '.fas')):
            # Will be handled by toolkit
            pass
        else:
            raise ValueError("MSA analysis requires multiple sequences or FASTA file")

    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    toolkit.load_model(args.model, args.model_path)

    results = toolkit.analyze_msa(
        msa_sequences=sequences,
        model=args.model,
        extract_consensus=args.extract_consensus,
        extract_conservation=args.extract_conservation,
        save_dir=args.save_dir
    )

    if args.save_dir:
        print(f"MSA analysis results saved to: {args.save_dir}")

    print_summary(results, "msa_analyze")


def cmd_metric_lddt(args):
    """Handle metric lddt command"""
    if not args.reference or not args.predicted:
        raise ValueError("Must specify both --reference and --predicted")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    
    # Parse distance thresholds
    if args.thresholds:
        thresholds = tuple(float(x) for x in args.thresholds.split(','))
    else:
        thresholds = (0.5, 1.0, 2.0, 4.0)
    
    results = toolkit.calculate_lddt(
        reference_structure=args.reference,
        predicted_structure=args.predicted,
        radius=args.radius,
        distance_thresholds=thresholds,
        return_column_scores=args.return_column_scores
    )
    
    if args.save_dir:
        save_output(results, args.save_dir, "lddt_results")
        print(f"LDDT results saved to: {args.save_dir}")
    
    print(f"Reference: {args.reference}")
    print(f"Predicted: {args.predicted}")
    print_summary(results, "metric_lddt")
    
    if args.return_column_scores and 'columns' in results:
        print(f"\nColumn scores available: {len(results['columns'])} residues")


def cmd_metric_rmsd(args):
    """Handle metric rmsd command"""
    if not args.file1 or not args.file2:
        raise ValueError("Must specify both --file1 and --file2")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    
    kwargs = {}
    if args.rotation:
        kwargs['rotation'] = args.rotation
    if args.file_format:
        kwargs['file_format'] = args.file_format
    if args.reorder:
        kwargs['reorder'] = True
        if args.reorder_method:
            kwargs['reorder_method'] = args.reorder_method
    if args.use_reflections:
        kwargs['use_reflections'] = True
    if args.use_reflections_keep_stereo:
        kwargs['use_reflections_keep_stereo'] = True
    if args.only_alpha_carbons:
        kwargs['only_alpha_carbons'] = True
    if args.ignore_hydrogen:
        kwargs['ignore_hydrogen'] = True
    if args.remove_idx:
        kwargs['remove_idx'] = [int(x) for x in args.remove_idx.split(',')]
    if args.add_idx:
        kwargs['add_idx'] = [int(x) for x in args.add_idx.split(',')]
    if args.output_aligned_structure:
        kwargs['output_aligned_structure'] = True
        if args.print_only_rmsd_atoms:
            kwargs['print_only_rmsd_atoms'] = True
    if args.gzip_format:
        kwargs['gzip_format'] = True
    
    results = toolkit.calculate_rmsd(args.file1, args.file2, **kwargs)
    
    if args.save_dir:
        if isinstance(results, str):
            # Aligned structure output
            output_file = Path(args.save_dir) / "aligned_structure.xyz"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(results)
            print(f"Aligned structure saved to: {output_file}")
        else:
            save_output({"rmsd": results}, args.save_dir, "rmsd_results")
            print(f"RMSD results saved to: {args.save_dir}")
    
    print(f"Structure 1: {args.file1}")
    print(f"Structure 2: {args.file2}")
    print_summary(results, "metric_rmsd")


def cmd_metric_tm_score(args):
    """Handle metric tm-score command"""
    if not args.struct1 or not args.struct2:
        raise ValueError("Must specify both --struct1 and --struct2")
    
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)
    
    kwargs = {}
    if args.mol:
        kwargs['mol'] = args.mol
    if args.score_type:
        kwargs['score_type'] = args.score_type
    if args.use_multithreading:
        kwargs['use_multithreading'] = True
    if args.d0:
        kwargs['d0'] = args.d0
    if args.output_aligned:
        kwargs['output_aligned'] = args.output_aligned
    
    results = toolkit.calculate_tm_score(args.struct1, args.struct2, **kwargs)
    
    if args.save_dir:
        save_output(results, args.save_dir, "tm_score_results")
        print(f"TM-score results saved to: {args.save_dir}")
    
    print(f"Structure 1: {args.struct1}")
    print(f"Structure 2: {args.struct2}")
    print_summary(results, "metric_tm_score")


def cmd_dataset_list(args):
    """Handle dataset list command"""
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)

    available_datasets = toolkit.list_available_datasets()
    print("Available Datasets:")
    for dataset in available_datasets:
        print(f" - {dataset}")


def cmd_dataset_download(args):
    """Handle dataset download command"""
    toolkit, config_loader = _get_toolkit(args.config_dir, args.device)

    print(f"Downloading dataset: {args.dataset}")
    if args.max_workers:
        toolkit.download_dataset(args.dataset, max_workers=args.max_workers)
    else:
        toolkit.download_dataset(args.dataset)

    print(f"Dataset '{args.dataset}' downloaded successfully")


def add_global_args(parser):
    """Add global arguments to a parser"""
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu',
                       help='Computing device (default: cpu)')
    parser.add_argument('--model', 
                       choices=['rna-fm', 'mrna-fm', 'rhofold', 'ribodiffusion', 'rhodesign', 'rna-msm'],
                       help='Model to use')
    parser.add_argument('--model-path',
                       help='Path to model checkpoint')
    parser.add_argument('--config-dir', default='configs',
                       help='Configuration directory (default: configs)')
    parser.add_argument('--provider-config',
                       help='Path to provider-specific configuration file')
    parser.add_argument('--seed', type=int,
                       help='Random seed')
    parser.add_argument('--save-dir',
                       help='Output directory for results')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')


def add_model_required_args(parser):
    """Add global arguments with required model to a parser"""
    add_global_args(parser)
    # Make model required for this parser
    for action in parser._actions:
        if action.dest == 'model':
            action.required = True


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='rnapy',
        description='RNA analysis toolkit command line interface'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # seq embed command
    seq_parser = subparsers.add_parser('seq', help='Sequence analysis commands')
    seq_subparsers = seq_parser.add_subparsers(dest='seq_command')

    embed_parser = seq_subparsers.add_parser('embed', help='Extract sequence embeddings')
    add_model_required_args(embed_parser)
    embed_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    embed_parser.add_argument('--fasta', help='FASTA file path')
    embed_parser.add_argument('--layer', type=int, default=-1,
                             help='Layer to extract from (default: -1)')
    embed_parser.add_argument('--format', choices=['raw', 'mean', 'bos'], default='mean',
                             help='Embedding format (default: mean)')

    compare_seq_parser = seq_subparsers.add_parser('compare', help='Compare RNA sequences')
    add_global_args(compare_seq_parser)
    compare_seq_parser.add_argument('--seqs', help='RNA sequences (comma-separated)')
    compare_seq_parser.add_argument('--seq1', help='First RNA sequence')
    compare_seq_parser.add_argument('--seq2', help='Second RNA sequence')

    recovery_parser = seq_subparsers.add_parser('recovery', help='Calculate sequence recovery rate')
    add_global_args(recovery_parser)
    recovery_parser.add_argument('--native', required=True, help='Native RNA sequence')
    recovery_parser.add_argument('--designed', required=True, help='Designed RNA sequence')

    # struct predict command
    struct_parser = subparsers.add_parser('struct', help='Structure prediction commands')
    struct_subparsers = struct_parser.add_subparsers(dest='struct_command')

    predict_parser = struct_subparsers.add_parser('predict', help='Predict RNA structure')
    add_model_required_args(predict_parser)
    predict_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    predict_parser.add_argument('--fasta', help='FASTA file path')
    predict_parser.add_argument('--structure-type', choices=['2d', '3d'],
                               help='Structure type (inferred from model if not specified)')

    compare_struct_parser = struct_subparsers.add_parser('compare', help='Compare RNA structures')
    add_global_args(compare_struct_parser)
    compare_struct_parser.add_argument('--struct1', required=True, help='First structure (dot-bracket format)')
    compare_struct_parser.add_argument('--struct2', required=True, help='Second structure (dot-bracket format)')

    f1_parser = struct_subparsers.add_parser('f1', help='Calculate structure F1 score')
    add_global_args(f1_parser)
    f1_parser.add_argument('--struct1', required=True, help='First structure (dot-bracket format)')
    f1_parser.add_argument('--struct2', required=True, help='Second structure (dot-bracket format)')

    # invfold gen command
    invfold_parser = subparsers.add_parser('invfold', help='Inverse folding commands')
    invfold_subparsers = invfold_parser.add_subparsers(dest='invfold_command')

    gen_parser = invfold_subparsers.add_parser('gen', help='Generate sequences from structure')
    add_model_required_args(gen_parser)
    gen_parser.add_argument('--pdb', required=True, help='PDB structure file')
    gen_parser.add_argument('--ss-npy', help='Secondary structure NPY file (for RhoDesign)')
    gen_parser.add_argument('--n-samples', type=int, default=1,
                           help='Number of sequences to generate (default: 1)')

    # msa commands
    msa_parser = subparsers.add_parser('msa', help='MSA analysis commands')
    msa_subparsers = msa_parser.add_subparsers(dest='msa_command')

    features_parser = msa_subparsers.add_parser('features', help='Extract MSA features')
    add_model_required_args(features_parser)
    features_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    features_parser.add_argument('--fasta', help='FASTA file path')
    features_parser.add_argument('--feature-type', choices=['embeddings', 'attention', 'both'],
                                default='embeddings', help='Feature type (default: embeddings)')
    features_parser.add_argument('--layer', type=int, default=-1,
                                help='Layer to extract from (default: -1)')

    analyze_parser = msa_subparsers.add_parser('analyze', help='Analyze MSA')
    add_model_required_args(analyze_parser)
    analyze_parser.add_argument('--seq', help='RNA sequence(s) (comma-separated for multiple)')
    analyze_parser.add_argument('--fasta', help='FASTA file path')
    analyze_parser.add_argument('--extract-consensus', action='store_true',
                               help='Extract consensus sequence')
    analyze_parser.add_argument('--extract-conservation', action='store_true',
                               help='Calculate conservation scores')

    # metric commands
    metric_parser = subparsers.add_parser('metric', help='Structure evaluation metrics')
    metric_subparsers = metric_parser.add_subparsers(dest='metric_command')

    # LDDT command
    lddt_parser = metric_subparsers.add_parser('lddt', help='Calculate LDDT score')
    add_global_args(lddt_parser)
    lddt_parser.add_argument('--reference', required=True, help='Reference structure file')
    lddt_parser.add_argument('--predicted', required=True, help='Predicted structure file')
    lddt_parser.add_argument('--radius', type=float, default=15.0, help='Distance radius (default: 15.0)')
    lddt_parser.add_argument('--thresholds', help='Distance thresholds (comma-separated, default: 0.5,1.0,2.0,4.0)')
    lddt_parser.add_argument('--return-column-scores', action='store_true', help='Return per-residue scores')

    # RMSD command
    rmsd_parser = metric_subparsers.add_parser('rmsd', help='Calculate RMSD')
    add_global_args(rmsd_parser)
    rmsd_parser.add_argument('--file1', required=True, help='First structure file')
    rmsd_parser.add_argument('--file2', required=True, help='Second structure file')
    rmsd_parser.add_argument('--rotation', choices=['kabsch', 'quaternion', 'none'], help='Rotation method')
    rmsd_parser.add_argument('--file-format', help='File format (auto-detected if not specified)')
    rmsd_parser.add_argument('--reorder', action='store_true', help='Reorder atoms')
    rmsd_parser.add_argument('--reorder-method', default='inertia-hungarian', help='Reorder method')
    rmsd_parser.add_argument('--use-reflections', action='store_true', help='Use reflections')
    rmsd_parser.add_argument('--use-reflections-keep-stereo', action='store_true', help='Use reflections keeping stereo')
    rmsd_parser.add_argument('--only-alpha-carbons', action='store_true', help='Only alpha carbons')
    rmsd_parser.add_argument('--ignore-hydrogen', action='store_true', help='Ignore hydrogen atoms')
    rmsd_parser.add_argument('--remove-idx', help='Remove atom indices (comma-separated)')
    rmsd_parser.add_argument('--add-idx', help='Add atom indices (comma-separated)')
    rmsd_parser.add_argument('--output-aligned-structure', action='store_true', help='Output aligned structure')
    rmsd_parser.add_argument('--print-only-rmsd-atoms', action='store_true', help='Print only RMSD atoms')
    rmsd_parser.add_argument('--gzip-format', action='store_true', help='Input is gzipped')

    # TM-score command
    tm_parser = metric_subparsers.add_parser('tm-score', help='Calculate TM-score')
    add_global_args(tm_parser)
    tm_parser.add_argument('--struct1', required=True, help='First structure file')
    tm_parser.add_argument('--struct2', required=True, help='Second structure file')
    tm_parser.add_argument('--mol', default='all', help='Molecule types (default: all)')
    tm_parser.add_argument('--score-type', choices=['t', 'r'], default='t', help='Score type (default: t)')
    tm_parser.add_argument('--use-multithreading', action='store_true', help='Use multithreading')
    tm_parser.add_argument('--d0', type=float, help='Custom d0 value')
    tm_parser.add_argument('--output-aligned', help='Save aligned structure to file')

    # dataset commands
    dataset_parser = subparsers.add_parser('dataset', help='Dataset commands')
    dataset_subparsers = dataset_parser.add_subparsers(dest='dataset_command')

    list_parser = dataset_subparsers.add_parser('list', help='List available datasets')
    add_global_args(list_parser)

    download_parser = dataset_subparsers.add_parser('download', help='Download a dataset')
    add_global_args(download_parser)
    download_parser.add_argument('--dataset', required=True, help='Dataset name or identifier')
    download_parser.add_argument('--max-workers', type=int,
                                help='Maximum number of workers for downloading')

    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    
    # Handle case where no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)

    # Handle missing subcommands
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Set random seed if provided
    if args.seed:
        import random
        import numpy as np
        random.seed(args.seed)
        np.random.seed(args.seed)

    try:
        if args.command == 'seq' and args.seq_command == 'embed':
            cmd_seq_embed(args)
        elif args.command == 'seq' and args.seq_command == 'compare':
            cmd_seq_compare(args)
        elif args.command == 'seq' and args.seq_command == 'recovery':
            cmd_seq_recovery(args)
        elif args.command == 'struct' and args.struct_command == 'predict':
            cmd_struct_predict(args)
        elif args.command == 'struct' and args.struct_command == 'compare':
            cmd_struct_compare(args)
        elif args.command == 'struct' and args.struct_command == 'f1':
            cmd_struct_f1(args)
        elif args.command == 'invfold' and args.invfold_command == 'gen':
            cmd_invfold_gen(args)
        elif args.command == 'msa' and args.msa_command == 'features':
            cmd_msa_features(args)
        elif args.command == 'msa' and args.msa_command == 'analyze':
            cmd_msa_analyze(args)
        elif args.command == 'metric' and args.metric_command == 'lddt':
            cmd_metric_lddt(args)
        elif args.command == 'metric' and args.metric_command == 'rmsd':
            cmd_metric_rmsd(args)
        elif args.command == 'metric' and args.metric_command == 'tm-score':
            cmd_metric_tm_score(args)
        elif args.command == 'dataset' and args.dataset_command == 'list':
            cmd_dataset_list(args)
        elif args.command == 'dataset' and args.dataset_command == 'download':
            cmd_dataset_download(args)
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        if args.verbose:
            raise
        else:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
