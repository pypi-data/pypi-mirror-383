# Environment wrapper script: nothing required

# ------------------------------------------------------------------------------------ #
#                                 Download Short Reads                                 #
# ------------------------------------------------------------------------------------ #
readonly SRR_ID

readonly READS_DIR=${WORK_EXP_SAMPLE_DIR}/reads
mkdir "$READS_DIR"

prefetch "$SRR_ID" --output-directory "$READS_DIR" # SRR_ID is set by tool bash init lines
fastq-dump --split-3 --outdir "$READS_DIR" "$READS_DIR/$SRR_ID"

readonly FASTQ_1=$READS_DIR/${SRR_ID}_1.fastq
readonly FASTQ_2=$READS_DIR/${SRR_ID}_2.fastq

gzip "$FASTQ_1"
readonly FASTQ_1_GZ=${FASTQ_1}.gz
gzip "$FASTQ_2"
readonly FASTQ_2_GZ=${FASTQ_2}.gz

# ------------------------------------------------------------------------------------ #
#                                    Assemble Reads                                    #
# ------------------------------------------------------------------------------------ #
unicycler -1 "$FASTQ_1_GZ" -2 "$FASTQ_2_GZ" -o "$WORK_EXP_SAMPLE_DIR" "${USER_TOOL_OPTIONS[@]}"

# ------------------------------------------------------------------------------------ #
#                               Compress Assembly Results                              #
# ------------------------------------------------------------------------------------ #
gzip "$WORK_EXP_SAMPLE_DIR/assembly.fasta"
gzip "$WORK_EXP_SAMPLE_DIR/assembly.gfa"

# ------------------------------------------------------------------------------------ #
#                                  Remove Short Reads                                  #
# ------------------------------------------------------------------------------------ #
rm -rf "$READS_DIR"
