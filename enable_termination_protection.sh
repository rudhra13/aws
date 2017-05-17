#query to check termiantion protection
for instance in `aws ec2 describe-instances \
  --query Reservations[*].Instances[*].InstanceId \
  | grep "i-" | cut -d\" -f 2`;
 do aws ec2 describe-instance-attribute \
  --instance-id $instance --attribute disableApiTermination \
  --query [InstanceId,DisableApiTermination]; 
done
##################################

# #query to enable one instance
# aws ec2 modify-instance-attribute --instance-id i-004b7ef5857deb61f --disable-api-termination
##################################
query to enable termination protection for all instances
for instance in `aws ec2 describe-instances --query Reservations[*].Instances[*].InstanceId | grep "i-" | cut -d\" -f 2`;
  do aws ec2 modify-instance-attribute --instance-id $instance --disable-api-termination; 
done
##################################
