# CDK Preinstalled Amazon Linux EC2 Instance Construct

This is a CDK Construct for creating a preinstalled AmazonLinux EC2 instance.

You can use Node.js, Visual Studio Code, git and other software as soon as the EC2 instance starts.

[![View on Construct Hub](https://constructs.dev/badge?package=cdk-preinstalled-amazon-linux-ec2)](https://constructs.dev/packages/cdk-preinstalled-amazon-linux-ec2)

[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/badmintoncryer/cdk-preinstalled-amazon-linux-ec2)
[![npm version](https://badge.fury.io/js/cdk-preinstalled-amazon-linux-ec2.svg)](https://badge.fury.io/js/cdk-preinstalled-amazon-linux-ec2)
[![Build Status](https://github.com/badmintoncryer/cdk-preinstalled-amazon-linux-ec2/actions/workflows/build.yml/badge.svg)](https://github.com/badmintoncryer/cdk-preinstalled-amazon-linux-ec2/actions/workflows/build.yml)
[![Release Status](https://github.com/badmintoncryer/cdk-preinstalled-amazon-linux-ec2/actions/workflows/release.yml/badge.svg)](https://github.com/badmintoncryer/cdk-preinstalled-amazon-linux-ec2/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![npm downloads](https://img.shields.io/npm/dt/cdk-preinstalled-amazon-linux-ec2.svg?style=flat)](https://www.npmjs.com/package/cdk-preinstalled-amazon-linux-ec2)

## Usage

Install the package:

```bash
npm install cdk-preinstalled-amazon-linux-ec2
```

Use it in your CDK stack:

```python
import { PreinstalledAmazonLinuxInstance } from 'cdk-preinstalled-amazon-linux-ec2';
import * as ec2 from 'aws-cdk-lib/aws-ec2';

declare const vpc: ec2.IVpc;

// You can configure all properties of the EC2 instance
new PreinstalledAmazonLinuxInstance(this, 'Instance', {
  vpc,
  instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.NANO),
  machineImage: new ec2.AmazonLinuxImage({
    generation: ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023,
  }),
  // Specify preinstalled software
  preinstalledSoftware: {
    packages: [
      PreinstalledSoftwareType.NODEJS,
      PreinstalledSoftwareType.VSCODE,
      PreinstalledSoftwareType.GIT,
    ],
    others: ['rsyslog'], // You can specify other software packages. These parameters are used as `sudo dnf install ${parameter}`
});
```

After the stack is deployed, you can SSH into the EC2 instance and use Node.js:

```bash
$ ssh ec2-user@<public-ip>
$ node --version
v20.13.1
$ code --version
1.89.1
$ git --version
git version 2.39.3
```

## user data

Installation of software is done by user data script. You can see the script in the `src/index.ts` file.

```python
// Install Node.js
userData.addCommands(
  'touch ~/.bashrc',
  'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash',
  'source ~/.bashrc',
  'export NVM_DIR="$HOME/.nvm"',
  '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"',
  `nvm install ${props.nodeJsVersion ?? '--lts'}`,
  // Note that the above will install nvm, node and npm for the root user.
  // It will not add the correct ENV VAR in ec2-user's environment.
  `cat <<EOF >> /home/ec2-user/.bashrc
export NVM_DIR="/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
EOF`);
```

Ofcourse, you can customize the additional user data script by calling `instance.userData.addCommands()` method.

```python
declare const instance: PreinstalledAmazonLinuxInstance;

// install yarn
instance.userData.addCommands(
  'npm install -g yarn'
);
```
