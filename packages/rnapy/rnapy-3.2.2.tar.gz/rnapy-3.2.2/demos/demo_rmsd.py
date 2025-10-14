from pathlib import Path
from textwrap import indent

from rnapy.toolkit import RNAToolkit


def angstrom(value: float) -> str:
	return f"{value:.3f} Å"


def preview_block(block: str, lines: int = 5) -> str:
	rows = [line for line in block.strip().splitlines() if line]
	return "\n".join(rows[:lines])


def main() -> None:
	demo_dir = Path(__file__).resolve().parent
	resources = demo_dir / "input" / "rmsd_tests" / "resources"
	toolkit = RNAToolkit()

	print("RNAToolkit RMSD showcase")

	pdb_a = resources / "ci2_1.pdb"
	pdb_b = resources / "ci2_2.pdb"
	rmsd_full = toolkit.calculate_rmsd(str(pdb_a), str(pdb_b), file_format="pdb")
	rmsd_ca = toolkit.calculate_rmsd(str(pdb_a), str(pdb_b), file_format="pdb", only_alpha_carbons=True)
	print(f"ci2 full-atom RMSD: {angstrom(rmsd_full)}")
	print(f"ci2 Cα-only RMSD: {angstrom(rmsd_ca)}")

	issue_a = resources / "issue78" / "a.xyz"
	issue_b = resources / "issue78" / "b.xyz"
	issue_rmsd = toolkit.calculate_rmsd(
		str(issue_a),
		str(issue_b),
		file_format="xyz",
		reorder=True,
		reorder_method="hungarian",
		use_reflections=True,
	)
	print(f"issue78 reordered RMSD: {angstrom(issue_rmsd)}")
	aligned = toolkit.calculate_rmsd(
		str(issue_a),
		str(issue_b),
		file_format="xyz",
		reorder=True,
		reorder_method="hungarian",
		use_reflections=True,
		output_aligned_structure=True,
		print_only_rmsd_atoms=True,
	)
	print("Aligned structure preview:")
	print(indent(preview_block(aligned), "    "))

	chem_a = resources / "CHEMBL3039407.xyz"
	chem_b = resources / "CHEMBL3039407_order.xyz"
	chem_plain = toolkit.calculate_rmsd(str(chem_a), str(chem_b), file_format="xyz", reorder=True)
	chem_filtered = toolkit.calculate_rmsd(
		str(chem_a),
		str(chem_b),
		file_format="xyz",
		reorder=True,
		ignore_hydrogen=True,
	)
	print(f"CHEMBL3039407 RMSD with hydrogens: {angstrom(chem_plain)}")
	print(f"CHEMBL3039407 RMSD no hydrogens: {angstrom(chem_filtered)}")

	ethane_ref = resources / "ethane.xyz"
	ethane_moved = resources / "ethane_translate.xyz"
	rmsd_quaternion = toolkit.calculate_rmsd(
		str(ethane_moved),
		str(ethane_ref),
		file_format="xyz",
		rotation="quaternion",
	)
	rmsd_none = toolkit.calculate_rmsd(
		str(ethane_moved),
		str(ethane_ref),
		file_format="xyz",
		rotation="none",
	)
	print(f"ethane quaternion RMSD: {angstrom(rmsd_quaternion)}")
	print(f"ethane no-rotation RMSD: {angstrom(rmsd_none)}")


if __name__ == "__main__":
	main()

