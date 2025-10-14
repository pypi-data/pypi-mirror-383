from Bio.Blast import NCBIXML

# Parse BLASTN result file
with open("blast_result.xml", "r") as result_file:
    blast_record = NCBIXML.read(result_file)

# Extract similarity percentage from the first alignment
similarity = blast_record.alignments[0].hsps[0].identities / blast_record.alignments[0].hsps[0].align_length * 100
print("Similarity: {:.2f}%".format(similarity))