"""
Cloud Deployment Manager
Handles deployment to AWS, GCP, Azure
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console

console = Console()

class CloudDeployment:
    """Manage cloud deployments"""
    
    def __init__(self, provider: str = "aws"):
        self.provider = provider
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load deployment configuration"""
        config_file = Path.home() / ".universal-memory" / "cloud-config.json"
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict):
        """Save deployment configuration"""
        config_dir = Path.home() / ".universal-memory"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "cloud-config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def deploy(self, region: str = "us-east-1"):
        """Deploy to cloud"""
        console.print(f"[bold]Deploying to {self.provider} ({region})...[/bold]")
        
        if self.provider == "aws":
            return self.deploy_aws(region)
        elif self.provider == "gcp":
            return self.deploy_gcp(region)
        elif self.provider == "azure":
            return self.deploy_azure(region)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def deploy_aws(self, region: str):
        """Deploy to AWS using ECS + RDS + ElastiCache + OpenSearch"""
        console.print("\n[bold cyan]AWS Deployment[/bold cyan]")
        
        # Check AWS CLI
        try:
            subprocess.run(["aws", "--version"], check=True, capture_output=True)
        except:
            console.print("[red]❌ AWS CLI not found. Install from: https://aws.amazon.com/cli/[/red]")
            return False
        
        console.print("[green]✅ AWS CLI found[/green]")
        
        # Create CloudFormation template
        template = self.generate_aws_template(region)
        
        # Deploy stack
        stack_name = "universal-ai-memory"
        console.print(f"\nDeploying CloudFormation stack: {stack_name}")
        
        template_file = Path("/tmp/universal-memory-stack.yaml")
        with open(template_file, "w") as f:
            f.write(template)
        
        try:
            subprocess.run([
                "aws", "cloudformation", "create-stack",
                "--stack-name", stack_name,
                "--template-body", f"file://{template_file}",
                "--region", region,
                "--capabilities", "CAPABILITY_IAM"
            ], check=True)
            
            console.print("[green]✅ Stack deployment initiated[/green]")
            console.print(f"\nMonitor progress:")
            console.print(f"  aws cloudformation describe-stacks --stack-name {stack_name} --region {region}")
            
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Deployment failed: {e}[/red]")
            return False
    
    def generate_aws_template(self, region: str) -> str:
        """Generate AWS CloudFormation template"""
        return """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Universal AI Memory - Production Deployment'

Parameters:
  VoyageAPIKey:
    Type: String
    NoEcho: true
    Description: Voyage AI API Key
  
  CohereAPIKey:
    Type: String
    NoEcho: true
    Description: Cohere API Key

Resources:
  # VPC
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: universal-memory-vpc

  # Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      MapPublicIpOnLaunch: true

  # RDS PostgreSQL
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for Universal Memory
      SubnetIds:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: universal-memory-db
      Engine: postgres
      EngineVersion: '16.1'
      DBInstanceClass: db.t3.micro
      AllocatedStorage: 20
      StorageType: gp3
      MasterUsername: postgres
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${DBSecret}:SecretString:password}}'
      DBSubnetGroupName: !Ref DBSubnetGroup
      PubliclyAccessible: true
      BackupRetentionPeriod: 7

  DBSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      GenerateSecretString:
        SecretStringTemplate: '{"username": "postgres"}'
        GenerateStringKey: password
        PasswordLength: 32

  # ElastiCache Redis
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for Redis
      SubnetIds:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2

  RedisCluster:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheNodeType: cache.t3.micro
      Engine: redis
      NumCacheNodes: 1
      CacheSubnetGroupName: !Ref CacheSubnetGroup

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: universal-memory-cluster

  # Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: universal-memory
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: 256
      Memory: 512
      ContainerDefinitions:
        - Name: universal-memory
          Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/universal-memory:latest'
          Environment:
            - Name: POSTGRES_HOST
              Value: !GetAtt Database.Endpoint.Address
            - Name: REDIS_HOST
              Value: !GetAtt RedisCluster.RedisEndpoint.Address
            - Name: VOYAGE_API_KEY
              Value: !Ref VoyageAPIKey
            - Name: COHERE_API_KEY
              Value: !Ref CohereAPIKey

Outputs:
  DatabaseEndpoint:
    Value: !GetAtt Database.Endpoint.Address
  RedisEndpoint:
    Value: !GetAtt RedisCluster.RedisEndpoint.Address
  ClusterName:
    Value: !Ref ECSCluster
"""
    
    def deploy_gcp(self, region: str):
        """Deploy to Google Cloud Platform"""
        console.print("\n[bold cyan]GCP Deployment[/bold cyan]")
        console.print("[yellow]Coming soon![/yellow]")
        return False
    
    def deploy_azure(self, region: str):
        """Deploy to Microsoft Azure"""
        console.print("\n[bold cyan]Azure Deployment[/bold cyan]")
        console.print("[yellow]Coming soon![/yellow]")
        return False
    
    def get_status(self) -> Dict:
        """Get deployment status"""
        if self.provider == "aws":
            return self.get_aws_status()
        return {}
    
    def get_aws_status(self) -> Dict:
        """Get AWS deployment status"""
        try:
            result = subprocess.run([
                "aws", "cloudformation", "describe-stacks",
                "--stack-name", "universal-ai-memory"
            ], capture_output=True, text=True, check=True)
            
            import json
            data = json.loads(result.stdout)
            stack = data["Stacks"][0]
            
            return {
                "status": stack["StackStatus"],
                "outputs": {o["OutputKey"]: o["OutputValue"] for o in stack.get("Outputs", [])}
            }
        except:
            return {"status": "NOT_DEPLOYED"}
    
    def destroy(self):
        """Destroy cloud deployment"""
        console.print(f"[bold red]Destroying {self.provider} deployment...[/bold red]")
        
        if self.provider == "aws":
            return self.destroy_aws()
        return False
    
    def destroy_aws(self):
        """Destroy AWS deployment"""
        try:
            subprocess.run([
                "aws", "cloudformation", "delete-stack",
                "--stack-name", "universal-ai-memory"
            ], check=True)
            
            console.print("[green]✅ Stack deletion initiated[/green]")
            return True
        except:
            console.print("[red]❌ Failed to delete stack[/red]")
            return False
