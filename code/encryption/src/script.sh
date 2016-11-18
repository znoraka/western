#!/bin/sh

# bool AC = true;
# bool DC = true;
# bool shuffleC = true;
# bool FIBS = false;
# bool xorOp = true;
# bool crcb = true;
# bool lum = true;


# mkdir -p $1/ac_dc_shuffle_fibs_xor_chrom_lum/
# ../bin/crypt $1/ac_dc_shuffle_fibs_xor_chrom_lum/ $2 --ac --dc --shuffle --fibs --xor --chrominance --luminance

# mkdir -p $1/ac_dc_shuffle_fibs_xor_lum/
# ../bin/crypt $1/ac_dc_shuffle_fibs_xor_lum/ $2 --ac --dc --shuffle --xor --luminance

# mkdir -p $1/ac_dc_shuffle_fibs_xor_chrom/
# ../bin/crypt $1/ac_dc_shuffle_fibs_xor_chrom/ $2 --ac --dc --shuffle --xor --chrominance

# mkdir -p $1/ac_dc_fibs_xor_chrom_lum/
# ../bin/crypt $1/ac_dc_fibs_xor_chrom_lum/ $2 --ac --dc --fibs --xor --chrominance --luminance

# mkdir -p $1/ac_fibs_xor_chrom_lum/
# ../bin/crypt $1/ac_fibs_xor_chrom_lum/ $2 --ac --fibs --xor --chrominance --luminance

# mkdir -p $1/ac_fibs_xor_lum/
# ../bin/crypt $1/ac_fibs_xor_lum/ $2 --ac --fibs --xor --luminance

# mkdir -p $1/dc_fibs_xor_chrom_lum/
# ../bin/crypt $1/dc_fibs_xor_chrom_lum/ $2 --dc --fibs --xor --chrominance --luminance

# mkdir -p $1/ac_fibs_xor_lum_shuffle/
# ../bin/crypt $1/ac_fibs_xor_lum_shuffle/ $2 --ac --fibs --xor --luminance --shuffle

# mkdir -p $1/ac_fibs_xor_lum_chrom_shuffle/
# ../bin/crypt $1/ac_fibs_xor_lum_chrom_shuffle/ $2 --ac --dc --fibs --xor --luminance --shuffle

# mkdir -p $1/ac_dc_shuffle_fibs_chrom_lum/
# ../bin/crypt $1/ac_dc_shuffle_fibs_chrom_lum/ $2 --ac --dc --shuffle --fibs --chrominance --luminance

mkdir -p $1/ac_dc_shuffle/
../bin/crypt $1/ac_dc_shuffle/ $2 --xor --luminance --ac --shuffle --chrominance
