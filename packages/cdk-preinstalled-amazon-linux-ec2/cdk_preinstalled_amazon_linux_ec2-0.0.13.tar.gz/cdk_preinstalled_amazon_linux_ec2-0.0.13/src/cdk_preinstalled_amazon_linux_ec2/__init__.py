r'''
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
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


class PreinstalledAmazonLinuxInstance(
    _aws_cdk_aws_ec2_ceddda9d.Instance,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-preinstalled-amazon-linux-ec2.PreinstalledAmazonLinuxInstance",
):
    '''Create an EC2 instance with preinstalled software.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        preinstalled_software: typing.Optional[typing.Union["PreinstalledSoftware", typing.Dict[builtins.str, typing.Any]]] = None,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
        detailed_monitoring: typing.Optional[builtins.bool] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
        init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        instance_name: typing.Optional[builtins.str] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        source_dest_check: typing.Optional[builtins.bool] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
        user_data_causes_replacement: typing.Optional[builtins.bool] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param preinstalled_software: The software to preinstall on the instance. Default: - no software is preinstalled
        :param instance_type: Type of instance to launch.
        :param machine_image: AMI to launch.
        :param vpc: VPC to launch the instance in.
        :param allow_all_ipv6_outbound: Whether the instance could initiate IPv6 connections to anywhere by default. This property is only used when you do not provide a security group. Default: false
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default. This property is only used when you do not provide a security group. Default: true
        :param associate_public_ip_address: Whether to associate a public IP address to the primary network interface attached to this instance. Default: - public IP address is automatically assigned based on default behavior
        :param availability_zone: In which AZ to place the instance within the VPC. Default: - Random zone.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param credit_specification: Specifying the CPU credit type for burstable EC2 instance types (T2, T3, T3a, etc). The unlimited CPU credit option is not supported for T3 instances with a dedicated host. Default: - T2 instances are standard, while T3, T4g, and T3a instances are unlimited.
        :param detailed_monitoring: Whether "Detailed Monitoring" is enabled for this instance Keep in mind that Detailed Monitoring results in extra charges. Default: - false
        :param ebs_optimized: Indicates whether the instance is optimized for Amazon EBS I/O. This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance. This optimization isn't available with all instance types. Additional usage charges apply when using an EBS-optimized instance. Default: false
        :param init: Apply the given CloudFormation Init configuration to the instance at startup. Default: - no CloudFormation init
        :param init_options: Use the given options for applying CloudFormation Init. Describes the configsets to use and the timeout to wait Default: - default options
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param key_name: (deprecated) Name of SSH keypair to grant access to instance. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Default: - No SSH access will be possible.
        :param placement_group: The placement group that you want to launch the instance into. Default: - no placement group will be used for this instance.
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param propagate_tags_to_volume_on_creation: Propagate the EC2 instance tags to the EBS volumes. Default: - false
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: - false
        :param resource_signal_timeout: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: Duration.minutes(5)
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param source_dest_check: Specifies whether to enable an instance launched in a VPC to perform NAT. This controls whether source/destination checking is enabled on the instance. A value of true means that checking is enabled, and false means that checking is disabled. The value must be false for the instance to perform NAT. Default: true
        :param ssm_session_permissions: Add SSM session permissions to the instance role. Setting this to ``true`` adds the necessary permissions to connect to the instance using SSM Session Manager. You can do this from the AWS Console. NOTE: Setting this flag to ``true`` may not be enough by itself. You must also use an AMI that comes with the SSM Agent, or install the SSM Agent yourself. See `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_ in the SSM Developer Guide. Default: false
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param user_data_causes_replacement: Changes to the UserData force replacement. Depending the EC2 instance type, changing UserData either restarts the instance or replaces the instance. - Instance store-backed instances are replaced. - EBS-backed instances are restarted. By default, restarting does not execute the new UserData so you will need a different mechanism to ensure the instance is restarted. Setting this to ``true`` will make the instance's Logical ID depend on the UserData, which will cause CloudFormation to replace it if the UserData changes. Default: - true iff ``initOptions`` is specified, false otherwise.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c9a1423334dfc78f723231d72b2d552a8bf34ab8b88aebe51ca10138593a85d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = PreinstalledAmazonLinuxInstanceProps(
            preinstalled_software=preinstalled_software,
            instance_type=instance_type,
            machine_image=machine_image,
            vpc=vpc,
            allow_all_ipv6_outbound=allow_all_ipv6_outbound,
            allow_all_outbound=allow_all_outbound,
            associate_public_ip_address=associate_public_ip_address,
            availability_zone=availability_zone,
            block_devices=block_devices,
            credit_specification=credit_specification,
            detailed_monitoring=detailed_monitoring,
            ebs_optimized=ebs_optimized,
            init=init,
            init_options=init_options,
            instance_name=instance_name,
            key_name=key_name,
            key_pair=key_pair,
            placement_group=placement_group,
            private_ip_address=private_ip_address,
            propagate_tags_to_volume_on_creation=propagate_tags_to_volume_on_creation,
            require_imdsv2=require_imdsv2,
            resource_signal_timeout=resource_signal_timeout,
            role=role,
            security_group=security_group,
            source_dest_check=source_dest_check,
            ssm_session_permissions=ssm_session_permissions,
            user_data=user_data,
            user_data_causes_replacement=user_data_causes_replacement,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-preinstalled-amazon-linux-ec2.PreinstalledAmazonLinuxInstanceProps",
    jsii_struct_bases=[_aws_cdk_aws_ec2_ceddda9d.InstanceProps],
    name_mapping={
        "instance_type": "instanceType",
        "machine_image": "machineImage",
        "vpc": "vpc",
        "allow_all_ipv6_outbound": "allowAllIpv6Outbound",
        "allow_all_outbound": "allowAllOutbound",
        "associate_public_ip_address": "associatePublicIpAddress",
        "availability_zone": "availabilityZone",
        "block_devices": "blockDevices",
        "credit_specification": "creditSpecification",
        "detailed_monitoring": "detailedMonitoring",
        "ebs_optimized": "ebsOptimized",
        "init": "init",
        "init_options": "initOptions",
        "instance_name": "instanceName",
        "key_name": "keyName",
        "key_pair": "keyPair",
        "placement_group": "placementGroup",
        "private_ip_address": "privateIpAddress",
        "propagate_tags_to_volume_on_creation": "propagateTagsToVolumeOnCreation",
        "require_imdsv2": "requireImdsv2",
        "resource_signal_timeout": "resourceSignalTimeout",
        "role": "role",
        "security_group": "securityGroup",
        "source_dest_check": "sourceDestCheck",
        "ssm_session_permissions": "ssmSessionPermissions",
        "user_data": "userData",
        "user_data_causes_replacement": "userDataCausesReplacement",
        "vpc_subnets": "vpcSubnets",
        "preinstalled_software": "preinstalledSoftware",
    },
)
class PreinstalledAmazonLinuxInstanceProps(_aws_cdk_aws_ec2_ceddda9d.InstanceProps):
    def __init__(
        self,
        *,
        instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
        machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        associate_public_ip_address: typing.Optional[builtins.bool] = None,
        availability_zone: typing.Optional[builtins.str] = None,
        block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
        credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
        detailed_monitoring: typing.Optional[builtins.bool] = None,
        ebs_optimized: typing.Optional[builtins.bool] = None,
        init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
        init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        instance_name: typing.Optional[builtins.str] = None,
        key_name: typing.Optional[builtins.str] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
        private_ip_address: typing.Optional[builtins.str] = None,
        propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
        require_imdsv2: typing.Optional[builtins.bool] = None,
        resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
        source_dest_check: typing.Optional[builtins.bool] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
        user_data_causes_replacement: typing.Optional[builtins.bool] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        preinstalled_software: typing.Optional[typing.Union["PreinstalledSoftware", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for PreinstalledAmazonLinuxInstance.

        :param instance_type: Type of instance to launch.
        :param machine_image: AMI to launch.
        :param vpc: VPC to launch the instance in.
        :param allow_all_ipv6_outbound: Whether the instance could initiate IPv6 connections to anywhere by default. This property is only used when you do not provide a security group. Default: false
        :param allow_all_outbound: Whether the instance could initiate connections to anywhere by default. This property is only used when you do not provide a security group. Default: true
        :param associate_public_ip_address: Whether to associate a public IP address to the primary network interface attached to this instance. Default: - public IP address is automatically assigned based on default behavior
        :param availability_zone: In which AZ to place the instance within the VPC. Default: - Random zone.
        :param block_devices: Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes. Each instance that is launched has an associated root device volume, either an Amazon EBS volume or an instance store volume. You can use block device mappings to specify additional EBS volumes or instance store volumes to attach to an instance when it is launched. Default: - Uses the block device mapping of the AMI
        :param credit_specification: Specifying the CPU credit type for burstable EC2 instance types (T2, T3, T3a, etc). The unlimited CPU credit option is not supported for T3 instances with a dedicated host. Default: - T2 instances are standard, while T3, T4g, and T3a instances are unlimited.
        :param detailed_monitoring: Whether "Detailed Monitoring" is enabled for this instance Keep in mind that Detailed Monitoring results in extra charges. Default: - false
        :param ebs_optimized: Indicates whether the instance is optimized for Amazon EBS I/O. This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance. This optimization isn't available with all instance types. Additional usage charges apply when using an EBS-optimized instance. Default: false
        :param init: Apply the given CloudFormation Init configuration to the instance at startup. Default: - no CloudFormation init
        :param init_options: Use the given options for applying CloudFormation Init. Describes the configsets to use and the timeout to wait Default: - default options
        :param instance_name: The name of the instance. Default: - CDK generated name
        :param key_name: (deprecated) Name of SSH keypair to grant access to instance. Default: - No SSH access will be possible.
        :param key_pair: The SSH keypair to grant access to the instance. Default: - No SSH access will be possible.
        :param placement_group: The placement group that you want to launch the instance into. Default: - no placement group will be used for this instance.
        :param private_ip_address: Defines a private IP address to associate with an instance. Private IP should be available within the VPC that the instance is build within. Default: - no association
        :param propagate_tags_to_volume_on_creation: Propagate the EC2 instance tags to the EBS volumes. Default: - false
        :param require_imdsv2: Whether IMDSv2 should be required on this instance. Default: - false
        :param resource_signal_timeout: The length of time to wait for the resourceSignalCount. The maximum value is 43200 (12 hours). Default: Duration.minutes(5)
        :param role: An IAM role to associate with the instance profile assigned to this Auto Scaling Group. The role must be assumable by the service principal ``ec2.amazonaws.com``: Default: - A role will automatically be created, it can be accessed via the ``role`` property
        :param security_group: Security Group to assign to this instance. Default: - create new security group
        :param source_dest_check: Specifies whether to enable an instance launched in a VPC to perform NAT. This controls whether source/destination checking is enabled on the instance. A value of true means that checking is enabled, and false means that checking is disabled. The value must be false for the instance to perform NAT. Default: true
        :param ssm_session_permissions: Add SSM session permissions to the instance role. Setting this to ``true`` adds the necessary permissions to connect to the instance using SSM Session Manager. You can do this from the AWS Console. NOTE: Setting this flag to ``true`` may not be enough by itself. You must also use an AMI that comes with the SSM Agent, or install the SSM Agent yourself. See `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_ in the SSM Developer Guide. Default: false
        :param user_data: Specific UserData to use. The UserData may still be mutated after creation. Default: - A UserData object appropriate for the MachineImage's Operating System is created.
        :param user_data_causes_replacement: Changes to the UserData force replacement. Depending the EC2 instance type, changing UserData either restarts the instance or replaces the instance. - Instance store-backed instances are replaced. - EBS-backed instances are restarted. By default, restarting does not execute the new UserData so you will need a different mechanism to ensure the instance is restarted. Setting this to ``true`` will make the instance's Logical ID depend on the UserData, which will cause CloudFormation to replace it if the UserData changes. Default: - true iff ``initOptions`` is specified, false otherwise.
        :param vpc_subnets: Where to place the instance within the VPC. Default: - Private subnets.
        :param preinstalled_software: The software to preinstall on the instance. Default: - no software is preinstalled
        '''
        if isinstance(init_options, dict):
            init_options = _aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions(**init_options)
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if isinstance(preinstalled_software, dict):
            preinstalled_software = PreinstalledSoftware(**preinstalled_software)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__334eb01c668e6ca9bfd6d599da22858b05b079eeea1e7b6a9f71ee632f092b87)
            check_type(argname="argument instance_type", value=instance_type, expected_type=type_hints["instance_type"])
            check_type(argname="argument machine_image", value=machine_image, expected_type=type_hints["machine_image"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument allow_all_ipv6_outbound", value=allow_all_ipv6_outbound, expected_type=type_hints["allow_all_ipv6_outbound"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument associate_public_ip_address", value=associate_public_ip_address, expected_type=type_hints["associate_public_ip_address"])
            check_type(argname="argument availability_zone", value=availability_zone, expected_type=type_hints["availability_zone"])
            check_type(argname="argument block_devices", value=block_devices, expected_type=type_hints["block_devices"])
            check_type(argname="argument credit_specification", value=credit_specification, expected_type=type_hints["credit_specification"])
            check_type(argname="argument detailed_monitoring", value=detailed_monitoring, expected_type=type_hints["detailed_monitoring"])
            check_type(argname="argument ebs_optimized", value=ebs_optimized, expected_type=type_hints["ebs_optimized"])
            check_type(argname="argument init", value=init, expected_type=type_hints["init"])
            check_type(argname="argument init_options", value=init_options, expected_type=type_hints["init_options"])
            check_type(argname="argument instance_name", value=instance_name, expected_type=type_hints["instance_name"])
            check_type(argname="argument key_name", value=key_name, expected_type=type_hints["key_name"])
            check_type(argname="argument key_pair", value=key_pair, expected_type=type_hints["key_pair"])
            check_type(argname="argument placement_group", value=placement_group, expected_type=type_hints["placement_group"])
            check_type(argname="argument private_ip_address", value=private_ip_address, expected_type=type_hints["private_ip_address"])
            check_type(argname="argument propagate_tags_to_volume_on_creation", value=propagate_tags_to_volume_on_creation, expected_type=type_hints["propagate_tags_to_volume_on_creation"])
            check_type(argname="argument require_imdsv2", value=require_imdsv2, expected_type=type_hints["require_imdsv2"])
            check_type(argname="argument resource_signal_timeout", value=resource_signal_timeout, expected_type=type_hints["resource_signal_timeout"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_group", value=security_group, expected_type=type_hints["security_group"])
            check_type(argname="argument source_dest_check", value=source_dest_check, expected_type=type_hints["source_dest_check"])
            check_type(argname="argument ssm_session_permissions", value=ssm_session_permissions, expected_type=type_hints["ssm_session_permissions"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument user_data_causes_replacement", value=user_data_causes_replacement, expected_type=type_hints["user_data_causes_replacement"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument preinstalled_software", value=preinstalled_software, expected_type=type_hints["preinstalled_software"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_type": instance_type,
            "machine_image": machine_image,
            "vpc": vpc,
        }
        if allow_all_ipv6_outbound is not None:
            self._values["allow_all_ipv6_outbound"] = allow_all_ipv6_outbound
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if associate_public_ip_address is not None:
            self._values["associate_public_ip_address"] = associate_public_ip_address
        if availability_zone is not None:
            self._values["availability_zone"] = availability_zone
        if block_devices is not None:
            self._values["block_devices"] = block_devices
        if credit_specification is not None:
            self._values["credit_specification"] = credit_specification
        if detailed_monitoring is not None:
            self._values["detailed_monitoring"] = detailed_monitoring
        if ebs_optimized is not None:
            self._values["ebs_optimized"] = ebs_optimized
        if init is not None:
            self._values["init"] = init
        if init_options is not None:
            self._values["init_options"] = init_options
        if instance_name is not None:
            self._values["instance_name"] = instance_name
        if key_name is not None:
            self._values["key_name"] = key_name
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if placement_group is not None:
            self._values["placement_group"] = placement_group
        if private_ip_address is not None:
            self._values["private_ip_address"] = private_ip_address
        if propagate_tags_to_volume_on_creation is not None:
            self._values["propagate_tags_to_volume_on_creation"] = propagate_tags_to_volume_on_creation
        if require_imdsv2 is not None:
            self._values["require_imdsv2"] = require_imdsv2
        if resource_signal_timeout is not None:
            self._values["resource_signal_timeout"] = resource_signal_timeout
        if role is not None:
            self._values["role"] = role
        if security_group is not None:
            self._values["security_group"] = security_group
        if source_dest_check is not None:
            self._values["source_dest_check"] = source_dest_check
        if ssm_session_permissions is not None:
            self._values["ssm_session_permissions"] = ssm_session_permissions
        if user_data is not None:
            self._values["user_data"] = user_data
        if user_data_causes_replacement is not None:
            self._values["user_data_causes_replacement"] = user_data_causes_replacement
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if preinstalled_software is not None:
            self._values["preinstalled_software"] = preinstalled_software

    @builtins.property
    def instance_type(self) -> _aws_cdk_aws_ec2_ceddda9d.InstanceType:
        '''Type of instance to launch.'''
        result = self._values.get("instance_type")
        assert result is not None, "Required property 'instance_type' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.InstanceType, result)

    @builtins.property
    def machine_image(self) -> _aws_cdk_aws_ec2_ceddda9d.IMachineImage:
        '''AMI to launch.'''
        result = self._values.get("machine_image")
        assert result is not None, "Required property 'machine_image' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IMachineImage, result)

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''VPC to launch the instance in.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def allow_all_ipv6_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance could initiate IPv6 connections to anywhere by default.

        This property is only used when you do not provide a security group.

        :default: false
        '''
        result = self._values.get("allow_all_ipv6_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''Whether the instance could initiate connections to anywhere by default.

        This property is only used when you do not provide a security group.

        :default: true
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def associate_public_ip_address(self) -> typing.Optional[builtins.bool]:
        '''Whether to associate a public IP address to the primary network interface attached to this instance.

        :default: - public IP address is automatically assigned based on default behavior
        '''
        result = self._values.get("associate_public_ip_address")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def availability_zone(self) -> typing.Optional[builtins.str]:
        '''In which AZ to place the instance within the VPC.

        :default: - Random zone.
        '''
        result = self._values.get("availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def block_devices(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]]:
        '''Specifies how block devices are exposed to the instance. You can specify virtual devices and EBS volumes.

        Each instance that is launched has an associated root device volume,
        either an Amazon EBS volume or an instance store volume.
        You can use block device mappings to specify additional EBS volumes or
        instance store volumes to attach to an instance when it is launched.

        :default: - Uses the block device mapping of the AMI

        :see: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/block-device-mapping-concepts.html
        '''
        result = self._values.get("block_devices")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.BlockDevice]], result)

    @builtins.property
    def credit_specification(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits]:
        '''Specifying the CPU credit type for burstable EC2 instance types (T2, T3, T3a, etc).

        The unlimited CPU credit option is not supported for T3 instances with a dedicated host.

        :default: - T2 instances are standard, while T3, T4g, and T3a instances are unlimited.
        '''
        result = self._values.get("credit_specification")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits], result)

    @builtins.property
    def detailed_monitoring(self) -> typing.Optional[builtins.bool]:
        '''Whether "Detailed Monitoring" is enabled for this instance Keep in mind that Detailed Monitoring results in extra charges.

        :default: - false

        :see: http://aws.amazon.com/cloudwatch/pricing/
        '''
        result = self._values.get("detailed_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ebs_optimized(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the instance is optimized for Amazon EBS I/O.

        This optimization provides dedicated throughput to Amazon EBS and an optimized configuration stack to provide optimal Amazon EBS I/O performance.
        This optimization isn't available with all instance types.
        Additional usage charges apply when using an EBS-optimized instance.

        :default: false
        '''
        result = self._values.get("ebs_optimized")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def init(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit]:
        '''Apply the given CloudFormation Init configuration to the instance at startup.

        :default: - no CloudFormation init
        '''
        result = self._values.get("init")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit], result)

    @builtins.property
    def init_options(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions]:
        '''Use the given options for applying CloudFormation Init.

        Describes the configsets to use and the timeout to wait

        :default: - default options
        '''
        result = self._values.get("init_options")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions], result)

    @builtins.property
    def instance_name(self) -> typing.Optional[builtins.str]:
        '''The name of the instance.

        :default: - CDK generated name
        '''
        result = self._values.get("instance_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) Name of SSH keypair to grant access to instance.

        :default: - No SSH access will be possible.

        :deprecated: - Use ``keyPair`` instead - https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2-readme.html#using-an-existing-ec2-key-pair

        :stability: deprecated
        '''
        result = self._values.get("key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_pair(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair]:
        '''The SSH keypair to grant access to the instance.

        :default: - No SSH access will be possible.
        '''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair], result)

    @builtins.property
    def placement_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup]:
        '''The placement group that you want to launch the instance into.

        :default: - no placement group will be used for this instance.
        '''
        result = self._values.get("placement_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup], result)

    @builtins.property
    def private_ip_address(self) -> typing.Optional[builtins.str]:
        '''Defines a private IP address to associate with an instance.

        Private IP should be available within the VPC that the instance is build within.

        :default: - no association
        '''
        result = self._values.get("private_ip_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def propagate_tags_to_volume_on_creation(self) -> typing.Optional[builtins.bool]:
        '''Propagate the EC2 instance tags to the EBS volumes.

        :default: - false
        '''
        result = self._values.get("propagate_tags_to_volume_on_creation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def require_imdsv2(self) -> typing.Optional[builtins.bool]:
        '''Whether IMDSv2 should be required on this instance.

        :default: - false
        '''
        result = self._values.get("require_imdsv2")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def resource_signal_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The length of time to wait for the resourceSignalCount.

        The maximum value is 43200 (12 hours).

        :default: Duration.minutes(5)
        '''
        result = self._values.get("resource_signal_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''An IAM role to associate with the instance profile assigned to this Auto Scaling Group.

        The role must be assumable by the service principal ``ec2.amazonaws.com``:

        :default: - A role will automatically be created, it can be accessed via the ``role`` property

        Example::

            const role = new iam.Role(this, 'MyRole', {
              assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com')
            });
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_group(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]:
        '''Security Group to assign to this instance.

        :default: - create new security group
        '''
        result = self._values.get("security_group")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup], result)

    @builtins.property
    def source_dest_check(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether to enable an instance launched in a VPC to perform NAT.

        This controls whether source/destination checking is enabled on the instance.
        A value of true means that checking is enabled, and false means that checking is disabled.
        The value must be false for the instance to perform NAT.

        :default: true
        '''
        result = self._values.get("source_dest_check")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ssm_session_permissions(self) -> typing.Optional[builtins.bool]:
        '''Add SSM session permissions to the instance role.

        Setting this to ``true`` adds the necessary permissions to connect
        to the instance using SSM Session Manager. You can do this
        from the AWS Console.

        NOTE: Setting this flag to ``true`` may not be enough by itself.
        You must also use an AMI that comes with the SSM Agent, or install
        the SSM Agent yourself. See
        `Working with SSM Agent <https://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html>`_
        in the SSM Developer Guide.

        :default: false
        '''
        result = self._values.get("ssm_session_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def user_data(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData]:
        '''Specific UserData to use.

        The UserData may still be mutated after creation.

        :default:

        - A UserData object appropriate for the MachineImage's
        Operating System is created.
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData], result)

    @builtins.property
    def user_data_causes_replacement(self) -> typing.Optional[builtins.bool]:
        '''Changes to the UserData force replacement.

        Depending the EC2 instance type, changing UserData either
        restarts the instance or replaces the instance.

        - Instance store-backed instances are replaced.
        - EBS-backed instances are restarted.

        By default, restarting does not execute the new UserData so you
        will need a different mechanism to ensure the instance is restarted.

        Setting this to ``true`` will make the instance's Logical ID depend on the
        UserData, which will cause CloudFormation to replace it if the UserData
        changes.

        :default: - true iff ``initOptions`` is specified, false otherwise.
        '''
        result = self._values.get("user_data_causes_replacement")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to place the instance within the VPC.

        :default: - Private subnets.
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def preinstalled_software(self) -> typing.Optional["PreinstalledSoftware"]:
        '''The software to preinstall on the instance.

        :default: - no software is preinstalled
        '''
        result = self._values.get("preinstalled_software")
        return typing.cast(typing.Optional["PreinstalledSoftware"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreinstalledAmazonLinuxInstanceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-preinstalled-amazon-linux-ec2.PreinstalledSoftware",
    jsii_struct_bases=[],
    name_mapping={"others": "others", "packages": "packages"},
)
class PreinstalledSoftware:
    def __init__(
        self,
        *,
        others: typing.Optional[typing.Sequence[builtins.str]] = None,
        packages: typing.Optional[typing.Sequence["PreinstalledSoftwarePackage"]] = None,
    ) -> None:
        '''The configuration for preinstalled software.

        :param others: Whether to install other software. This is a list of software to install and passed to ``dnf install <software>`` Default: - no other software is preinstalled
        :param packages: The type of preinstalled software. Default: - no software is preinstalled
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__657dec901feded435d209f20ab5a0de458a54fdf89665912ea70cb5dfd6220fa)
            check_type(argname="argument others", value=others, expected_type=type_hints["others"])
            check_type(argname="argument packages", value=packages, expected_type=type_hints["packages"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if others is not None:
            self._values["others"] = others
        if packages is not None:
            self._values["packages"] = packages

    @builtins.property
    def others(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Whether to install other software.

        This is a list of software to install and passed to ``dnf install <software>``

        :default: - no other software is preinstalled
        '''
        result = self._values.get("others")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def packages(self) -> typing.Optional[typing.List["PreinstalledSoftwarePackage"]]:
        '''The type of preinstalled software.

        :default: - no software is preinstalled
        '''
        result = self._values.get("packages")
        return typing.cast(typing.Optional[typing.List["PreinstalledSoftwarePackage"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PreinstalledSoftware(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-preinstalled-amazon-linux-ec2.PreinstalledSoftwarePackage")
class PreinstalledSoftwarePackage(enum.Enum):
    '''The type of preinstalled software.'''

    NODEJS = "NODEJS"
    '''Node.js.'''
    DOCKER = "DOCKER"
    '''Docker.'''
    VSCODE = "VSCODE"
    '''Visual Studio Code.'''
    GIT = "GIT"
    '''Git.'''


__all__ = [
    "PreinstalledAmazonLinuxInstance",
    "PreinstalledAmazonLinuxInstanceProps",
    "PreinstalledSoftware",
    "PreinstalledSoftwarePackage",
]

publication.publish()

def _typecheckingstub__5c9a1423334dfc78f723231d72b2d552a8bf34ab8b88aebe51ca10138593a85d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    preinstalled_software: typing.Optional[typing.Union[PreinstalledSoftware, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    availability_zone: typing.Optional[builtins.str] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
    detailed_monitoring: typing.Optional[builtins.bool] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
    init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_name: typing.Optional[builtins.str] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
    private_ip_address: typing.Optional[builtins.str] = None,
    propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    source_dest_check: typing.Optional[builtins.bool] = None,
    ssm_session_permissions: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    user_data_causes_replacement: typing.Optional[builtins.bool] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__334eb01c668e6ca9bfd6d599da22858b05b079eeea1e7b6a9f71ee632f092b87(
    *,
    instance_type: _aws_cdk_aws_ec2_ceddda9d.InstanceType,
    machine_image: _aws_cdk_aws_ec2_ceddda9d.IMachineImage,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_ipv6_outbound: typing.Optional[builtins.bool] = None,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    associate_public_ip_address: typing.Optional[builtins.bool] = None,
    availability_zone: typing.Optional[builtins.str] = None,
    block_devices: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.BlockDevice, typing.Dict[builtins.str, typing.Any]]]] = None,
    credit_specification: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CpuCredits] = None,
    detailed_monitoring: typing.Optional[builtins.bool] = None,
    ebs_optimized: typing.Optional[builtins.bool] = None,
    init: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.CloudFormationInit] = None,
    init_options: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.ApplyCloudFormationInitOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    instance_name: typing.Optional[builtins.str] = None,
    key_name: typing.Optional[builtins.str] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    placement_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IPlacementGroup] = None,
    private_ip_address: typing.Optional[builtins.str] = None,
    propagate_tags_to_volume_on_creation: typing.Optional[builtins.bool] = None,
    require_imdsv2: typing.Optional[builtins.bool] = None,
    resource_signal_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_group: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup] = None,
    source_dest_check: typing.Optional[builtins.bool] = None,
    ssm_session_permissions: typing.Optional[builtins.bool] = None,
    user_data: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.UserData] = None,
    user_data_causes_replacement: typing.Optional[builtins.bool] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    preinstalled_software: typing.Optional[typing.Union[PreinstalledSoftware, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__657dec901feded435d209f20ab5a0de458a54fdf89665912ea70cb5dfd6220fa(
    *,
    others: typing.Optional[typing.Sequence[builtins.str]] = None,
    packages: typing.Optional[typing.Sequence[PreinstalledSoftwarePackage]] = None,
) -> None:
    """Type checking stubs"""
    pass
