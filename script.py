import boto3
import pandas as pd

# List of regions to fetch instances from
regions = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "ap-south-1", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
    "ap-southeast-1", "ap-southeast-2",
    "ca-central-1",
    "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3",
    "eu-north-1",  
    "sa-east-1"
]

# Prepare a list to store instance data
instances_list = []

for region in regions:
    # Initialize AWS EC2 Client for each region
    ec2_client = boto3.client("ec2", region_name=region)

    # Fetch instance details
    response = ec2_client.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            # Check if the instance is in the running state
            if instance["State"]["Name"] == "running":
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                availability_zone = instance["Placement"]["AvailabilityZone"]
                lifecycle = instance.get("InstanceLifecycle", "On-demand")  # Spot instances have this field
                image_id = instance["ImageId"]  # AMI ID

                # Fetch instance name tag (if exists)
                name_tag = next(
                    (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), 
                    "Unknown"
                )

                # Normalize lifecycle field
                lifecycle = "spot" if lifecycle.lower() == "spot" else "On-demand"

                # Fetch AMI Name
                try:
                    ami_response = ec2_client.describe_images(ImageIds=[image_id])
                    ami_name = ami_response["Images"][0]["Name"] if ami_response["Images"] else "Unknown"
                except Exception as e:
                    ami_name = "Unknown"

                # Append to list
                instances_list.append([region, availability_zone, name_tag, instance_id, instance_type, lifecycle, image_id, ami_name])

# Convert to DataFrame
df = pd.DataFrame(instances_list, columns=["Region", "Availability Zone", "Instance Name", "Instance ID", "Instance Type", "Lifecycle", "AMI ID", "AMI Name"])

# Display DataFrame
print(df)

# Save to CSV (optional)
df.to_csv("instances_list.csv", index=False)
