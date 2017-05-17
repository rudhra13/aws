#!/bin/bash
## __AUTHOR : RUDHRA RAI __##

# First configure the region in aws configure 
# for which you have to take the snapshot

cat << EOM
		+-----------------------------------------+
		|Creating snapshots of available instances|
		|	within the given region		  |
		+-----------------------------------------+
EOM

# Getting the list of volumes which are available in the given region
Region="$1"
list=$(aws ec2 describe-volumes --region $Region --query 'Volumes[?State==`available`]')

#  Transfering list data to vol-desc json file
echo $list > vol-desc.json

# creating array of volume Ids
arrId=`echo $(jq -r '.[].VolumeId' vol-desc.json)`;
Id=($arrId)

# Iterator variable for iterating the loop
iterateId=($arrId);

# Array for volume types
arrType=`echo $(jq -r '.[].VolumeType' vol-desc.json)`;
Type=($arrType);

# Array for volume Iops
arrIops=`echo $(jq -r '.[].Iops' vol-desc.json)`;
Iops=($arrIops);

# Array for volume Size
arrSize=`echo $(jq -r '.[].Size' vol-desc.json)`;
Size=($arrSize);

# Array for Cration time of the volume
arrTime=`echo $(jq -r '.[].CreateTime' vol-desc.json)`;
Time=($arrTime);


# Looping by volume id 
# such that by every volume id create the snapshot of the volume
# and put the description as
# Volume Id, Type, Number of Iops, Size of Volume and Time at which volume was created

for((i=0;i<${#iterateId[@]};i++))
do 
	aws ec2 create-snapshot --volume-id ${iterateId[$i]} --description "${Id[$i]} - ${Type[$i]} -${Iops[$i]} - ${Size[$i]}gb - ${Time[$i]}"; 
done

