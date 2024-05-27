import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as cfn from 'aws-cdk-lib/aws-cloudformation';

export class RaGstackStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create an S3 bucket for hosting the static website
    const siteBucket = new s3.Bucket(this, 'MyStaticSiteBucket', {
      bucketName:"secure-insurance-website",
      websiteIndexDocument: 'index.html',
      autoDeleteObjects: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      blockPublicAccess: {
        blockPublicAcls: true,
        ignorePublicAcls: true,
        restrictPublicBuckets: false,
        blockPublicPolicy: false,
      } 
    });

    // Define a bucket policy to allow public read access
    const bucketPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:GetObject'],
      principals: [new iam.AnyPrincipal()],
      resources: [siteBucket.arnForObjects('*')],
    });

    // Add the bucket policy to the bucket
    siteBucket.addToResourcePolicy(bucketPolicy);
    
    // Deploy the contents of the 'website' directory to the S3 bucket
    new s3deploy.BucketDeployment(this, 'DeployStaticSite', {
      sources: [s3deploy.Source.asset('./website')],
      destinationBucket: siteBucket,
    });
     

    // Create an S3 bucket named 'rag-bot-source'
    const sourceBucket = new s3.Bucket(this, 'RagSourceBucket', {
      bucketName: 'rag-bot-source',
      removalPolicy: cdk.RemovalPolicy.DESTROY // Optional: Specifies what happens to the bucket when the stack is deleted. Use with caution.
    });

    // Create an IAM role for the Lambda function
    const lambdaRole = new iam.Role(this, 'LambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
    });

    // Attach policies to the role to grant permissions for S3 read operations
    lambdaRole.addToPolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject','s3:PutObject'],
      resources: [sourceBucket.bucketArn + '/*'], // Allow access to all objects in the bucket
    }));

    // Add the necessary managed policies to the Lambda role
    lambdaRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'));
    lambdaRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));

    // Function to create embeddings and save to S3
    const dockerFunc = new lambda.DockerImageFunction(this, "DockerFunc", {
      code: lambda.DockerImageCode.fromImageAsset("./image"),
      memorySize: 1024,
      timeout: cdk.Duration.seconds(20),
      architecture: lambda.Architecture.X86_64,
      role: lambdaRole,
    });

    // Grant the Lambda function permission to read from the source S3 bucket
    sourceBucket.grantRead(dockerFunc);

    // Add S3 event notification to trigger the Lambda function when a document is added to the 'docs' folder
    sourceBucket.addEventNotification(s3.EventType.OBJECT_CREATED, new s3n.LambdaDestination(dockerFunc), {
      prefix: 'docs/',
    });

    // Generate function URL
    const functionUrl = dockerFunc.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
        allowedOrigins: ["*"],
      },
    });

    // Output the function URL
    new cdk.CfnOutput(this, "FunctionUrlValue", {
      value: functionUrl.url,
    });
  }
}
