r'''
# Amazon AppFlow Construct Library

<!--BEGIN STABILITY BANNER-->---


![Experimental](https://img.shields.io/badge/experimental-important.svg?style=for-the-badge)

> **Experimental:** This construct library is experimental and under active development.
> It is subject to non-backward compatible changes or removal in any future version.
> These are not subject to the [Semantic Versioning](https://semver.org/) model and
> breaking changes will be announced in the release notes. This means that while you may use them,
> you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Introduction

Amazon AppFlow is a service that enables creating managed, bi-directional data transfer integrations between various SaaS applications and AWS services.

For more information, see the [Amazon AppFlow User Guide](https://docs.aws.amazon.com/appflow/latest/userguide/what-is-appflow.html).

## Supported Applications

This library provides L2 constructs for the following applications and services:

* Amazon RDS for PostgreSQL (destination)
* Asana (source)
* EventBridge (destination)
* GitHub (source)
* Google Ads (source)
* Google Analytics 4 (source)
* Google BigQuery (source)
* HubSpot (source, destination)
* Mailchimp (source)
* Marketo (source)
* Microsoft Dynamics 365 (source)
* Microsoft SharePoint Online (source)
* Redshift (destination)
* S3 (source, destination)
* Salesforce (source, destination)
* Salesforce Marketing Cloud (source)
* SAP OData (source, destination)
* ServiceNow (source)
* Slack (source)
* Snowflake (destination)
* Zendesk (source)

## Example

```python
from aws_cdk import SecretValue
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_secretsmanager import ISecret
from cdklabs.cdk_appflow import ISource, IDestination, Filter, FilterCondition, Mapping, OnDemandFlow, S3Destination, SalesforceConnectorProfile, SalesforceSource, Transform, Validation, ValidationAction, ValidationCondition

# client_secret: ISecret
# access_token: SecretValue
# refresh_token: SecretValue
# instance_url: str


profile = SalesforceConnectorProfile(self, "MyConnectorProfile",
    o_auth=SalesforceOAuthSettings(
        access_token=access_token,
        flow=SalesforceOAuthFlow(
            refresh_token_grant=SalesforceOAuthRefreshTokenGrantFlow(
                refresh_token=refresh_token,
                client=client_secret
            )
        )
    ),
    instance_url=instance_url,
    is_sandbox=False
)

source = SalesforceSource(
    profile=profile,
    object="Account"
)

bucket = Bucket(self, "DestinationBucket")

destination = S3Destination(
    location=S3Location(bucket=bucket)
)

OnDemandFlow(self, "SfAccountToS3",
    source=source,
    destination=destination,
    mappings=[Mapping.map_all()],
    transforms=[
        Transform.mask(Field(name="Name"), "*")
    ],
    validations=[
        Validation.when(ValidationCondition.is_null("Name"), ValidationAction.ignore_record())
    ],
    filters=[
        Filter.when(FilterCondition.timestamp_less_than_equals(Field(name="LastModifiedDate", data_type="datetime"), Date(Date.parse("2022-02-02"))))
    ]
)
```

# Concepts

Amazon AppFlow introduces several concepts that abstract away the technicalities of setting up and managing data integrations.

An `Application` is any SaaS data integration component that can be either a *source* or a *destination* for Amazon AppFlow. A source is an application from which Amazon AppFlow will retrieve data, whereas a destination is an application to which Amazon AppFlow will send data.

A `Flow` is Amazon AppFlow's integration between a source and a destination.

A `ConnectorProfile` is Amazon AppFlow's abstraction over authentication/authorization with a particular SaaS application. The per-SaaS application permissions given to a particular `ConnectorProfile` will determine whether the connector profile can support the application as a source or as a destination (see whether a particular application is supported as either a source or a destination in [the documentation](https://docs.aws.amazon.com/appflow/latest/userguide/app-specific.html)).

## Types of Flows

The library introduces three, separate types of flows:

* `OnDemandFlow` - a construct representing a flow that can be triggered programmatically with the use of a [StartFlow API call](https://docs.aws.amazon.com/appflow/1.0/APIReference/API_StartFlow.html).
* `OnEventFlow` - a construct representing a flow that is triggered by a SaaS application event published to AppFlow. At the time of writing only a Salesforce source is able to publish events that can be consumed by AppFlow flows.
* `OnScheduleFlow` - a construct representing a flow that is triggered on a [`Schedule`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_events.Schedule.html)

## Tasks

Tasks are steps that can be taken upon fields. Tasks compose higher level objects that in this library are named `Operations`. There are four operations identified:

* Transforms - 1-1 transforms on source fields, like truncation or masking
* Mappings - 1-1 or many-to-1 operations from source fields to a destination field
* Filters - operations that limit the source data on particular conditions
* Validations - operations that work on a per-record level and can have either a record-level consequence (i.e. dropping the record) or a global one (terminating the flow).

Each flow exposes dedicated properties to each of the operation types that one can use like in the example below:

```python
from cdklabs.cdk_appflow import Filter, FilterCondition, IDestination, ISource, Mapping, OnDemandFlow, S3Destination, SalesforceConnectorProfile, SalesforceSource, Transform, Validation, ValidationAction, ValidationCondition

# stack: Stack
# source: ISource
# destination: IDestination


flow = OnDemandFlow(stack, "OnDemandFlow",
    source=source,
    destination=destination,
    transforms=[
        Transform.mask(Field(name="Name"), "*")
    ],
    mappings=[
        Mapping.map(Field(name="Name", data_type="String"), name="Name", data_type="string")
    ],
    filters=[
        Filter.when(FilterCondition.timestamp_less_than_equals(Field(name="LastModifiedDate", data_type="datetime"), Date(Date.parse("2022-02-02"))))
    ],
    validations=[
        Validation.when(ValidationCondition.is_null("Name"), ValidationAction.ignore_record())
    ]
)
```

## Monitoring

### Metrics

Each flow allows to access metrics through the methods:

* `metricFlowExecutionsStarted`
* `metricFlowExecutionsFailed`
* `metricFlowExecutionsSucceeded`
* `metricFlowExecutionTime`
* `metricFlowExecutionRecordsProcessed`

For detailed information about AppFlow metrics refer to [the documentation](https://docs.aws.amazon.com/appflow/latest/userguide/monitoring-cloudwatch.html).

It can be consumed by CloudWatch alarms as in the example below:

```python
from cdklabs.cdk_appflow import IFlow

# flow: IFlow
# stack: Stack


metric = flow.metric_flow_executions_started()

metric.create_alarm(stack, "FlowExecutionsStartedAlarm",
    threshold=1000,
    evaluation_periods=2
)
```

### EventBridge notifications

Each flow publishes events to the default EventBridge bus:

* `onRunStarted`
* `onRunCompleted`
* `onDeactivated` (only for the `OnEventFlow` and the `OnScheduleFlow`)
* `onStatus` (only for the `OnEventFlow` )

This way one can consume the notifications as in the example below:

```python
from aws_cdk.aws_sns import ITopic
from aws_cdk.aws_events_targets import SnsTopic
from cdklabs.cdk_appflow import IFlow

# flow: IFlow
# my_topic: ITopic


flow.on_run_completed("OnRunCompleted",
    target=SnsTopic(my_topic)
)
```

# Notable distinctions from CloudFormation specification

## `OnScheduleFlow` and `incrementalPullConfig`

In CloudFormation the definition of the `incrementalPullConfig` (which effectively gives a name of the field used for tracking the last pulled timestamp) is on the [`SourceFlowConfig`](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-appflow-flow-sourceflowconfig.html#cfn-appflow-flow-sourceflowconfig-incrementalpullconfig) property. In the library this has been moved to the `OnScheduleFlow` constructor properties.

## `S3Destination` and Glue Catalog

Although in CloudFormation the Glue Catalog configuration is settable on the flow level - it works only when the destination is S3. That is why the library shifts the Glue Catalog properties definition to the `S3Destination`, which in turn requires using Lazy for populating `metadataCatalogConfig` in the flow.

# Security considerations

It is *recommended* to follow [data protection mechanisms for Amazon AppFlow](https://docs.aws.amazon.com/appflow/latest/userguide/data-protection.html).

## Confidential information

Amazon AppFlow application integration is done using `ConnectionProfiles`. A `ConnectionProfile` requires providing sensitive information in the form of e.g. access and refresh tokens. It is *recommended* that such information is stored securely and passed to AWS CDK securely. All sensitive fields are effectively `IResolvable` and this means they can be resolved at deploy time. With that one should follow the [best practices for credentials with CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/security-best-practices.html#creds). In this library, the sensitive fields are typed as `SecretValue` to emphasize these should not be plain strings.

An example of using a predefined AWS Secrets Manager secret for storing sensitive information can be found below:

```python
from aws_cdk.aws_secretsmanager import Secret
from cdklabs.cdk_appflow import GoogleAnalytics4ConnectorProfile

# stack: Stack


secret = Secret.from_secret_name_v2(stack, "GA4Secret", "appflow/ga4")

profile = GoogleAnalytics4ConnectorProfile(stack, "GA4Connector",
    o_auth=GoogleAnalytics4OAuthSettings(
        flow=GoogleAnalytics4OAuthFlow(
            refresh_token_grant=GoogleAnalytics4RefreshTokenGrantFlow(
                refresh_token=secret.secret_value_from_json("refreshToken"),
                client_id=secret.secret_value_from_json("clientId"),
                client_secret=secret.secret_value_from_json("clientSecret")
            )
        )
    )
)
```

## An approach to managing permissions

This library relies on an internal `AppFlowPermissionsManager` class to automatically infer and apply appropriate resource policy statements to the S3 Bucket, KMS Key, and Secrets Manager Secret resources. `AppFlowPermissionsManager` places the statements exactly once for the `appflow.amazonaws.com` principal no matter how many times a resource is reused in the code.

### Confused Deputy Problem

Amazon AppFlow is an account-bound and a regional service. With this it is invulnerable to the confused deputy problem (see, e.g. [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html)). However, `AppFlowPermissionsManager` still introduces the `aws:SourceAccount` condition to the resource policies as a *best practice*.

## Upgrading and breaking changes

Please consult the [UPGRADING docs](/UPGRADING.md) for information.
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
import aws_cdk.aws_appflow as _aws_cdk_aws_appflow_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_glue_alpha as _aws_cdk_aws_glue_alpha_ce674d29
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_redshift_alpha as _aws_cdk_aws_redshift_alpha_9727f5af
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.AmazonRdsForPostgreSqlBasicAuthSettings",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class AmazonRdsForPostgreSqlBasicAuthSettings:
    def __init__(
        self,
        *,
        password: _aws_cdk_ceddda9d.SecretValue,
        username: builtins.str,
    ) -> None:
        '''(experimental) Basic authentication settings for the AmazonRdsForPostgreSqlConnectorProfile.

        :param password: (experimental) The password of the identity used for interacting with the Amazon RDS for PostgreSQL.
        :param username: (experimental) The username of the identity used for interacting with the Amazon RDS for PostgreSQL.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96e3255e9267c9a22750bc9922aeb173dcb6bc4bb8b2ffc75d4eb899f747d161)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''(experimental) The password of the identity used for interacting with the Amazon RDS for PostgreSQL.

        :stability: experimental
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) The username of the identity used for interacting with the Amazon RDS for PostgreSQL.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmazonRdsForPostgreSqlBasicAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.AmazonRdsForPostgreSqlDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "api_version": "apiVersion",
        "error_handling": "errorHandling",
    },
)
class AmazonRdsForPostgreSqlDestinationProps:
    def __init__(
        self,
        *,
        object: typing.Union["AmazonRdsForPostgreSqlObject", typing.Dict[builtins.str, typing.Any]],
        profile: "AmazonRdsForPostgreSqlConnectorProfile",
        api_version: typing.Optional[builtins.str] = None,
        error_handling: typing.Optional[typing.Union["ErrorHandlingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties of the AmazonRdsForPostgreSqlDestination.

        :param object: (experimental) The destination object table to write to.
        :param profile: (experimental) The profile to use with the destination.
        :param api_version: (experimental) The Amazon AppFlow Api Version.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        if isinstance(object, dict):
            object = AmazonRdsForPostgreSqlObject(**object)
        if isinstance(error_handling, dict):
            error_handling = ErrorHandlingConfiguration(**error_handling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f725757438cce70c8bc12ec03c1a8c12b32e2a6f3fe7ec3769638361956d149b)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument error_handling", value=error_handling, expected_type=type_hints["error_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if api_version is not None:
            self._values["api_version"] = api_version
        if error_handling is not None:
            self._values["error_handling"] = error_handling

    @builtins.property
    def object(self) -> "AmazonRdsForPostgreSqlObject":
        '''(experimental) The destination object table to write to.

        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast("AmazonRdsForPostgreSqlObject", result)

    @builtins.property
    def profile(self) -> "AmazonRdsForPostgreSqlConnectorProfile":
        '''(experimental) The profile to use with the destination.

        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("AmazonRdsForPostgreSqlConnectorProfile", result)

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The Amazon AppFlow Api Version.

        :stability: experimental
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def error_handling(self) -> typing.Optional["ErrorHandlingConfiguration"]:
        '''(experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the destination.

        For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        result = self._values.get("error_handling")
        return typing.cast(typing.Optional["ErrorHandlingConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmazonRdsForPostgreSqlDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.AmazonRdsForPostgreSqlObject",
    jsii_struct_bases=[],
    name_mapping={"schema": "schema", "table": "table"},
)
class AmazonRdsForPostgreSqlObject:
    def __init__(self, *, schema: builtins.str, table: builtins.str) -> None:
        '''(experimental) The definition of the Amazon AppFlow object for Amazon RDS for PostgreSQL.

        :param schema: (experimental) PostgreSQL schema name of the table.
        :param table: (experimental) PostgreSQL table name.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c725a2a36b9f4a2b583c74c11e02a973fee96febd089ef6e106e6e173726e21)
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "schema": schema,
            "table": table,
        }

    @builtins.property
    def schema(self) -> builtins.str:
        '''(experimental) PostgreSQL schema name of the table.

        :stability: experimental
        '''
        result = self._values.get("schema")
        assert result is not None, "Required property 'schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table(self) -> builtins.str:
        '''(experimental) PostgreSQL table name.

        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmazonRdsForPostgreSqlObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.AsanaSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "api_version": "apiVersion",
    },
)
class AsanaSourceProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        profile: "AsanaConnectorProfile",
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a10110e387fc84d27f617a32384b0edaf667147be8413bf5dccb7aa2c9a600a)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if api_version is not None:
            self._values["api_version"] = api_version

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "AsanaConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("AsanaConnectorProfile", result)

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AsanaSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.ConnectionMode")
class ConnectionMode(enum.Enum):
    '''
    :stability: experimental
    '''

    PUBLIC = "PUBLIC"
    '''
    :stability: experimental
    '''
    PRIVATE = "PRIVATE"
    '''
    :stability: experimental
    :internal: true
    '''


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.ConnectorAuthenticationType")
class ConnectorAuthenticationType(enum.Enum):
    '''
    :stability: experimental
    '''

    APIKEY = "APIKEY"
    '''
    :stability: experimental
    '''
    BASIC = "BASIC"
    '''
    :stability: experimental
    '''
    CUSTOM = "CUSTOM"
    '''
    :stability: experimental
    '''
    OAUTH2 = "OAUTH2"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ConnectorProfileProps",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "name": "name"},
)
class ConnectorProfileProps:
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d2b41de7a95f2c15f3a2e708fae5b91cad064354f541d048f25529a389dc9a8)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ConnectorType(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ConnectorType",
):
    '''
    :stability: experimental
    '''

    def __init__(self, name: builtins.str, is_custom: builtins.bool) -> None:
        '''
        :param name: -
        :param is_custom: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dedf196b2eb8984e508697aeef563f4abe76df9549bc1abbd76ea89b5090ced3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument is_custom", value=is_custom, expected_type=type_hints["is_custom"])
        jsii.create(self.__class__, self, [name, is_custom])

    @builtins.property
    @jsii.member(jsii_name="asProfileConnectorType")
    def as_profile_connector_type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "asProfileConnectorType"))

    @builtins.property
    @jsii.member(jsii_name="asTaskConnectorOperatorOrigin")
    def as_task_connector_operator_origin(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "asTaskConnectorOperatorOrigin"))

    @builtins.property
    @jsii.member(jsii_name="isCustom")
    def is_custom(self) -> builtins.bool:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "isCustom"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def _name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="asProfileConnectorLabel")
    def as_profile_connector_label(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "asProfileConnectorLabel"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.DataPullConfig",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "timestamp_field": "timestampField"},
)
class DataPullConfig:
    def __init__(
        self,
        *,
        mode: "DataPullMode",
        timestamp_field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mode: 
        :param timestamp_field: (experimental) The name of the field to use as a timestamp for recurring incremental flows. The default field is set per particular

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9a219093b3770ee1eb01f8ea621bdc4d6af591bcd53b51d77b6cd192fe4df56)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument timestamp_field", value=timestamp_field, expected_type=type_hints["timestamp_field"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mode": mode,
        }
        if timestamp_field is not None:
            self._values["timestamp_field"] = timestamp_field

    @builtins.property
    def mode(self) -> "DataPullMode":
        '''
        :stability: experimental
        '''
        result = self._values.get("mode")
        assert result is not None, "Required property 'mode' is missing"
        return typing.cast("DataPullMode", result)

    @builtins.property
    def timestamp_field(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the field to use as a timestamp for recurring incremental flows.

        The default field is set per particular

        :see: ISource.
        :stability: experimental
        '''
        result = self._values.get("timestamp_field")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataPullConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.DataPullMode")
class DataPullMode(enum.Enum):
    '''
    :stability: experimental
    '''

    COMPLETE = "COMPLETE"
    '''
    :stability: experimental
    '''
    INCREMENTAL = "INCREMENTAL"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ErrorHandlingConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "error_location": "errorLocation",
        "fail_on_first_error": "failOnFirstError",
    },
)
class ErrorHandlingConfiguration:
    def __init__(
        self,
        *,
        error_location: typing.Optional[typing.Union["S3Location", typing.Dict[builtins.str, typing.Any]]] = None,
        fail_on_first_error: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param error_location: 
        :param fail_on_first_error: 

        :stability: experimental
        '''
        if isinstance(error_location, dict):
            error_location = S3Location(**error_location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b902b20c49881b25e7253d2906d885c0512a58520c7a25f90d4e3da6113fc57c)
            check_type(argname="argument error_location", value=error_location, expected_type=type_hints["error_location"])
            check_type(argname="argument fail_on_first_error", value=fail_on_first_error, expected_type=type_hints["fail_on_first_error"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if error_location is not None:
            self._values["error_location"] = error_location
        if fail_on_first_error is not None:
            self._values["fail_on_first_error"] = fail_on_first_error

    @builtins.property
    def error_location(self) -> typing.Optional["S3Location"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("error_location")
        return typing.cast(typing.Optional["S3Location"], result)

    @builtins.property
    def fail_on_first_error(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("fail_on_first_error")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ErrorHandlingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.EventBridgeDestinationProps",
    jsii_struct_bases=[],
    name_mapping={"partner_bus": "partnerBus", "error_handling": "errorHandling"},
)
class EventBridgeDestinationProps:
    def __init__(
        self,
        *,
        partner_bus: builtins.str,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) The properties for the EventBridge destination.

        :param partner_bus: 
        :param error_handling: 

        :stability: experimental
        '''
        if isinstance(error_handling, dict):
            error_handling = ErrorHandlingConfiguration(**error_handling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ee9438969865bad2afd0571f058aa9ce19717393528c2a3f61f5b7b1f1e29c1)
            check_type(argname="argument partner_bus", value=partner_bus, expected_type=type_hints["partner_bus"])
            check_type(argname="argument error_handling", value=error_handling, expected_type=type_hints["error_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "partner_bus": partner_bus,
        }
        if error_handling is not None:
            self._values["error_handling"] = error_handling

    @builtins.property
    def partner_bus(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("partner_bus")
        assert result is not None, "Required property 'partner_bus' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def error_handling(self) -> typing.Optional[ErrorHandlingConfiguration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("error_handling")
        return typing.cast(typing.Optional[ErrorHandlingConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventBridgeDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EventSources(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.EventSources",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="salesforceEventSource")
    @builtins.classmethod
    def salesforce_event_source(
        cls,
        suffix: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''
        :param suffix: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05a2218bf349477bb87b155c2ac98cf73f23b1d586a50056874c4baf9ed0d409)
            check_type(argname="argument suffix", value=suffix, expected_type=type_hints["suffix"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "salesforceEventSource", [suffix]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.Field",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "data_type": "dataType"},
)
class Field:
    def __init__(
        self,
        *,
        name: builtins.str,
        data_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param data_type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c577310c8c6e1b3811a8040d35a1af0afda03b22fc2c2924cdb61a990adfb5c6)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument data_type", value=data_type, expected_type=type_hints["data_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if data_type is not None:
            self._values["data_type"] = data_type

    @builtins.property
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_type(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Field(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FilterCondition(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.FilterCondition",
):
    '''(experimental) A representation of a filter operation condtiion on a source record field.

    :stability: experimental
    '''

    def __init__(
        self,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        filter: builtins.str,
        properties: typing.Sequence[typing.Union["TaskProperty", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param field: -
        :param filter: -
        :param properties: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16baec51c19521c7c18d8fe59a8371588c6a927e50a836c930d9ebf33876dda6)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument filter", value=filter, expected_type=type_hints["filter"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        jsii.create(self.__class__, self, [field, filter, properties])

    @jsii.member(jsii_name="booleanEquals")
    @builtins.classmethod
    def boolean_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[builtins.bool, typing.Sequence[builtins.bool]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a875f6b5f7bf87a4f177870de2e0fafb24e434a660936970e77fc3d0c659d5f3)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "booleanEquals", [field, val]))

    @jsii.member(jsii_name="booleanNotEquals")
    @builtins.classmethod
    def boolean_not_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[builtins.bool, typing.Sequence[builtins.bool]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa94007128b06e5433d43cbaaf5c9378035abd60112ffe8d58c870c9b8e299b6)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "booleanNotEquals", [field, val]))

    @jsii.member(jsii_name="numberEquals")
    @builtins.classmethod
    def number_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[jsii.Number, typing.Sequence[jsii.Number]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ac4b1ff70f65e3e1219f41182dc75ee9e7ef453ba07b91b395813f9cbec231)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "numberEquals", [field, val]))

    @jsii.member(jsii_name="numberGreaterThan")
    @builtins.classmethod
    def number_greater_than(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: jsii.Number,
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__290508e525c94bd401dcfe60655c0c6d59a50149a374f408ba135bf3b4ff64b5)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "numberGreaterThan", [field, val]))

    @jsii.member(jsii_name="numberGreaterThanEquals")
    @builtins.classmethod
    def number_greater_than_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: jsii.Number,
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4afeedbae2168afc195222b93567587fa83ec21e60fbf57686855c6fe38f493e)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "numberGreaterThanEquals", [field, val]))

    @jsii.member(jsii_name="numberLessThan")
    @builtins.classmethod
    def number_less_than(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: jsii.Number,
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ca157f12d69a9aaf9ecb1bd1106e099d1e02e7fb48142c43d5e59a94da2b122)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "numberLessThan", [field, val]))

    @jsii.member(jsii_name="numberLessThanEquals")
    @builtins.classmethod
    def number_less_than_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: jsii.Number,
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31008f1be0a65f5601c54b82706f09a63fde99745a72ff0146f4c3a0a5e1f15d)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "numberLessThanEquals", [field, val]))

    @jsii.member(jsii_name="numberNotEquals")
    @builtins.classmethod
    def number_not_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[jsii.Number, typing.Sequence[jsii.Number]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c33472102821a812d20b857c2f029eebed54a9c9feab807739a4ace1ad3957c3)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "numberNotEquals", [field, val]))

    @jsii.member(jsii_name="stringContains")
    @builtins.classmethod
    def string_contains(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[builtins.str, typing.Sequence[builtins.str]],
    ) -> "FilterCondition":
        '''(experimental) A condition testing whether a string-type source field contains the given value(s).

        NOTE: When multiple values are passed the evaluation is resolved as logical OR

        :param field: a source field of a string type.
        :param val: a value (or values) to be contained by the field value.

        :return: an instance of a

        :see: FilterCondition
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1e674adc3eb5dea2e21b7980e89b87e7cd32b22ab3dafc8f2516cc2d576acce)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "stringContains", [field, val]))

    @jsii.member(jsii_name="stringEquals")
    @builtins.classmethod
    def string_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[builtins.str, typing.Sequence[builtins.str]],
    ) -> "FilterCondition":
        '''(experimental) A condition testing whether a string-type source field equals the given value(s).

        NOTE: When multiple values are passed the evaluation is resolved as logical OR

        :param field: a source field of a string type.
        :param val: a value (or values) to be contained by the field value.

        :return: an instance of a

        :see: FilterCondition
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e84b1e1d02ac2c57996ef297a0120f2460eb95456333571b6516b3ae2c568a72)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "stringEquals", [field, val]))

    @jsii.member(jsii_name="stringNotEquals")
    @builtins.classmethod
    def string_not_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[builtins.str, typing.Sequence[builtins.str]],
    ) -> "FilterCondition":
        '''(experimental) A condition testing whether a string-type source field does not equal the given value(s).

        NOTE: When multiple values are passed the evaluation is resolved as logical OR

        :param field: a source field of a string type.
        :param val: a value (or values) to be contained by the field value.

        :return: an instance of a

        :see: FilterCondition
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb2d9d82e577a11bb47b45cc1005652cb6590a0fcfc6fe5e0aff16460086f5f3)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "stringNotEquals", [field, val]))

    @jsii.member(jsii_name="timestampBetween")
    @builtins.classmethod
    def timestamp_between(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        lower: datetime.datetime,
        upper: datetime.datetime,
    ) -> "FilterCondition":
        '''
        :param field: -
        :param lower: -
        :param upper: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6596d56f873254bdbea91a961316b1e426193af89f30b1d81b619372eeaba594)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument lower", value=lower, expected_type=type_hints["lower"])
            check_type(argname="argument upper", value=upper, expected_type=type_hints["upper"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "timestampBetween", [field, lower, upper]))

    @jsii.member(jsii_name="timestampEquals")
    @builtins.classmethod
    def timestamp_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd22a2d553e04e7657f1cf1a5e834335d624cb0dddf2fae9d4f8cf34efbf41a4)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "timestampEquals", [field, val]))

    @jsii.member(jsii_name="timestampGreaterThan")
    @builtins.classmethod
    def timestamp_greater_than(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51b57011b2256e9228bd257aa6cd547ab315844abe8729773fefaa85e62dbb3e)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "timestampGreaterThan", [field, val]))

    @jsii.member(jsii_name="timestampGreaterThanEquals")
    @builtins.classmethod
    def timestamp_greater_than_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fe6c0395d580587e6d9c96e598196454ceb9a1817e3b6265dd3b775a6fce72d)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "timestampGreaterThanEquals", [field, val]))

    @jsii.member(jsii_name="timestampLessThan")
    @builtins.classmethod
    def timestamp_less_than(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8afdbe101b79fa52a1e42a99869170a0c6b15655d14267d75bc25bd8a03b69c6)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "timestampLessThan", [field, val]))

    @jsii.member(jsii_name="timestampLessThanEquals")
    @builtins.classmethod
    def timestamp_less_than_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c17beb7ddb040f7920e6fc36db02c529105115c35fac145e62bb6584c13d00c)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "timestampLessThanEquals", [field, val]))

    @jsii.member(jsii_name="timestampNotEquals")
    @builtins.classmethod
    def timestamp_not_equals(
        cls,
        field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
    ) -> "FilterCondition":
        '''
        :param field: -
        :param val: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9499e24c9ac13e1d29a6a235699b246a24118d09cc7e401e1ad201e82f4734c2)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument val", value=val, expected_type=type_hints["val"])
        return typing.cast("FilterCondition", jsii.sinvoke(cls, "timestampNotEquals", [field, val]))

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> Field:
        '''
        :stability: experimental
        '''
        return typing.cast(Field, jsii.get(self, "field"))

    @builtins.property
    @jsii.member(jsii_name="filter")
    def filter(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "filter"))

    @builtins.property
    @jsii.member(jsii_name="properties")
    def properties(self) -> typing.List["TaskProperty"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["TaskProperty"], jsii.get(self, "properties"))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.FlowProps",
    jsii_struct_bases=[],
    name_mapping={
        "destination": "destination",
        "mappings": "mappings",
        "source": "source",
        "description": "description",
        "filters": "filters",
        "key": "key",
        "name": "name",
        "transforms": "transforms",
        "validations": "validations",
    },
)
class FlowProps:
    def __init__(
        self,
        *,
        destination: "IDestination",
        mappings: typing.Sequence["IMapping"],
        source: "ISource",
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence["IFilter"]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence["ITransform"]] = None,
        validations: typing.Optional[typing.Sequence["IValidation"]] = None,
    ) -> None:
        '''
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63e0314fa809fbb27cb2cb0dde8fe14293f94bc3d6910858bdd4063c08568061)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument transforms", value=transforms, expected_type=type_hints["transforms"])
            check_type(argname="argument validations", value=validations, expected_type=type_hints["validations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
            "mappings": mappings,
            "source": source,
        }
        if description is not None:
            self._values["description"] = description
        if filters is not None:
            self._values["filters"] = filters
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if transforms is not None:
            self._values["transforms"] = transforms
        if validations is not None:
            self._values["validations"] = validations

    @builtins.property
    def destination(self) -> "IDestination":
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("IDestination", result)

    @builtins.property
    def mappings(self) -> typing.List["IMapping"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List["IMapping"], result)

    @builtins.property
    def source(self) -> "ISource":
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("ISource", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List["IFilter"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List["IFilter"]], result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transforms(self) -> typing.Optional[typing.List["ITransform"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("transforms")
        return typing.cast(typing.Optional[typing.List["ITransform"]], result)

    @builtins.property
    def validations(self) -> typing.Optional[typing.List["IValidation"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("validations")
        return typing.cast(typing.Optional[typing.List["IValidation"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FlowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.FlowStatus")
class FlowStatus(enum.Enum):
    '''
    :stability: experimental
    '''

    ACTIVE = "ACTIVE"
    '''
    :stability: experimental
    '''
    SUSPENDED = "SUSPENDED"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.FlowType")
class FlowType(enum.Enum):
    '''
    :stability: experimental
    '''

    EVENT = "EVENT"
    '''
    :stability: experimental
    '''
    ON_DEMAND = "ON_DEMAND"
    '''
    :stability: experimental
    '''
    SCHEDULED = "SCHEDULED"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.GitHubApiVersion")
class GitHubApiVersion(enum.Enum):
    '''(experimental) An enum representing the GitHub API versions.

    :stability: experimental
    '''

    V3 = "V3"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GitHubBasicAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "personal_access_token": "personalAccessToken",
        "username": "username",
    },
)
class GitHubBasicAuthSettings:
    def __init__(
        self,
        *,
        personal_access_token: _aws_cdk_ceddda9d.SecretValue,
        username: builtins.str,
    ) -> None:
        '''(experimental) GitHub Basic Authentication settings using Personal Access Token.

        :param personal_access_token: (experimental) Personal Access Token for GitHub authentication.
        :param username: (experimental) GitHub username.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e268fe526bd12af421247f3a5e384e1b9df12194d12e6d23107fed19bd5c45d5)
            check_type(argname="argument personal_access_token", value=personal_access_token, expected_type=type_hints["personal_access_token"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "personal_access_token": personal_access_token,
            "username": username,
        }

    @builtins.property
    def personal_access_token(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''(experimental) Personal Access Token for GitHub authentication.

        :stability: experimental
        '''
        result = self._values.get("personal_access_token")
        assert result is not None, "Required property 'personal_access_token' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) GitHub username.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubBasicAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GitHubConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "basic_auth": "basicAuth",
        "o_auth": "oAuth",
    },
)
class GitHubConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        basic_auth: typing.Optional[typing.Union[GitHubBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        o_auth: typing.Optional[typing.Union["GitHubOAuthSettings", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param basic_auth: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(basic_auth, dict):
            basic_auth = GitHubBasicAuthSettings(**basic_auth)
        if isinstance(o_auth, dict):
            o_auth = GitHubOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61bc30b75d8ced92cd18e268f5591ba2f236cfdd046af8185ebe39c6855e419d)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth
        if o_auth is not None:
            self._values["o_auth"] = o_auth

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def basic_auth(self) -> typing.Optional[GitHubBasicAuthSettings]:
        '''
        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional[GitHubBasicAuthSettings], result)

    @builtins.property
    def o_auth(self) -> typing.Optional["GitHubOAuthSettings"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        return typing.cast(typing.Optional["GitHubOAuthSettings"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GitHubOAuthEndpoints",
    jsii_struct_bases=[],
    name_mapping={"token": "token"},
)
class GitHubOAuthEndpoints:
    def __init__(self, *, token: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) GitHub's OAuth token and authorization endpoints.

        :param token: (experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ba14b32a0e8e2d79bdd5878a23ddee7374ed93c567a68e6b4ee82b692d52458)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubOAuthEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GitHubOAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class GitHubOAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["GitHubRefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Represents the OAuth flow enabled for GitHub.

        :param refresh_token_grant: (experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = GitHubRefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e31caa73fa95f06c2d89229e70b0c6cf337104851cd7e90d10041810b5c00623)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "GitHubRefreshTokenGrantFlow":
        '''(experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("GitHubRefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubOAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GitHubOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={"access_token": "accessToken", "endpoints": "endpoints"},
)
class GitHubOAuthSettings:
    def __init__(
        self,
        *,
        access_token: _aws_cdk_ceddda9d.SecretValue,
        endpoints: typing.Optional[typing.Union[GitHubOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: (experimental) The access token to be used when interacting with GitHub. Note: Currently only non-expiring access tokens are supported as "User access tokens that expire are currently an optional feature and are subject to change."
        :param endpoints: (experimental) The OAuth token and authorization endpoints.

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = GitHubOAuthEndpoints(**endpoints)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab80f2151f523ffcee8042372b826ee33d7f4ba5aefc8b2bbb09f2ac154eb4f0)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_token": access_token,
        }
        if endpoints is not None:
            self._values["endpoints"] = endpoints

    @builtins.property
    def access_token(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''(experimental) The access token to be used when interacting with GitHub.

        Note: Currently only non-expiring access tokens are supported as
        "User access tokens that expire are currently an optional feature and are subject to change."

        :stability: experimental
        '''
        result = self._values.get("access_token")
        assert result is not None, "Required property 'access_token' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def endpoints(self) -> typing.Optional[GitHubOAuthEndpoints]:
        '''(experimental) The OAuth token and authorization endpoints.

        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[GitHubOAuthEndpoints], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GitHubRefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class GitHubRefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''(experimental) The OAuth elements required for the execution of the refresh token grant flow.

        :param client_id: (experimental) The id of the client app.
        :param client_secret: (experimental) The secret of the client app.
        :param refresh_token: (experimental) A non-expired refresh token.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d48e31e276996840860d7f9db140adf67c361f51fa5d3cacf8b5e94e1f332074)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The id of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The secret of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) A non-expired refresh token.

        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubRefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GitHubSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class GitHubSourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: "GitHubConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Google Analytics v4 Source.

        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9254d787e0613946edeb3abac41d0e02b840f68b1b72eb07a1e019c201ee8fa3)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "GitHubConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("GitHubConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.GoogleAdsApiVersion")
class GoogleAdsApiVersion(enum.Enum):
    '''(experimental) An enum representing the GoogleAds API versions.

    :stability: experimental
    '''

    V16 = "V16"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "api_version": "apiVersion",
        "developer_token": "developerToken",
        "o_auth": "oAuth",
        "manager_id": "managerID",
    },
)
class GoogleAdsConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        api_version: builtins.str,
        developer_token: _aws_cdk_ceddda9d.SecretValue,
        o_auth: typing.Union["GoogleAdsOAuthSettings", typing.Dict[builtins.str, typing.Any]],
        manager_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param api_version: 
        :param developer_token: 
        :param o_auth: 
        :param manager_id: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = GoogleAdsOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d68581f43587a9b8d6c670235a257a8aac675685d0cb70a93e18a159c31d1fa)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument developer_token", value=developer_token, expected_type=type_hints["developer_token"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
            check_type(argname="argument manager_id", value=manager_id, expected_type=type_hints["manager_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "developer_token": developer_token,
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if manager_id is not None:
            self._values["manager_id"] = manager_id

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def developer_token(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("developer_token")
        assert result is not None, "Required property 'developer_token' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def o_auth(self) -> "GoogleAdsOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("GoogleAdsOAuthSettings", result)

    @builtins.property
    def manager_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("manager_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAdsConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsOAuthEndpoints",
    jsii_struct_bases=[],
    name_mapping={"authorization": "authorization", "token": "token"},
)
class GoogleAdsOAuthEndpoints:
    def __init__(
        self,
        *,
        authorization: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Google's OAuth token and authorization endpoints.

        :param authorization: (experimental) The OAuth authorization endpoint URI.
        :param token: (experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b866abeabb5b404df587566da5ca60fc80ed7309f2ed1dc61e3f33fda4058aa)
            check_type(argname="argument authorization", value=authorization, expected_type=type_hints["authorization"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if authorization is not None:
            self._values["authorization"] = authorization
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def authorization(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth authorization endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("authorization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAdsOAuthEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsOAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class GoogleAdsOAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["GoogleAdsRefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Represents the OAuth flow enabled for the GoogleAds.

        :param refresh_token_grant: (experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = GoogleAdsRefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d30be5ccf5bd5361e1685a3876eb56ea080887d90a0ba458775383c32bdb5071)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "GoogleAdsRefreshTokenGrantFlow":
        '''(experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("GoogleAdsRefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAdsOAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "endpoints": "endpoints",
        "flow": "flow",
    },
)
class GoogleAdsOAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        endpoints: typing.Optional[typing.Union[GoogleAdsOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
        flow: typing.Optional[typing.Union[GoogleAdsOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: (experimental) The access token to be used when interacting with Google Ads. Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired Default: Retrieves a fresh accessToken with the information in the [flow property]{@link GoogleAdsOAuthSettings#flow }
        :param endpoints: (experimental) The OAuth token and authorization endpoints.
        :param flow: (experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired. Default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = GoogleAdsOAuthEndpoints(**endpoints)
        if isinstance(flow, dict):
            flow = GoogleAdsOAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ae01841af763bdb713516e7577ae0fd5949d5c91f72b7bc25c5630b03049456)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The access token to be used when interacting with Google Ads.

        Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired

        :default: Retrieves a fresh accessToken with the information in the [flow property]{@link GoogleAdsOAuthSettings#flow }

        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def endpoints(self) -> typing.Optional[GoogleAdsOAuthEndpoints]:
        '''(experimental) The OAuth token and authorization endpoints.

        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[GoogleAdsOAuthEndpoints], result)

    @builtins.property
    def flow(self) -> typing.Optional[GoogleAdsOAuthFlow]:
        '''(experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired.

        :default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[GoogleAdsOAuthFlow], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAdsOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsRefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class GoogleAdsRefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''(experimental) The OAuth elements required for the execution of the refresh token grant flow.

        :param client_id: (experimental) The id of the client app.
        :param client_secret: (experimental) The secret of the client app.
        :param refresh_token: (experimental) A non-expired refresh token.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b4e3831023822364458e04692fe7434b8e23e7e6b259c8c24606bec1ffaaae)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The id of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The secret of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) A non-expired refresh token.

        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAdsRefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class GoogleAdsSourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: "GoogleAdsConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Google Ads Source.

        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96d3c97ac705591fcb0ee8e54809772b14e34c3ff09101140a14f17f16ced25f)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "GoogleAdsConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("GoogleAdsConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAdsSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4ApiVersion")
class GoogleAnalytics4ApiVersion(enum.Enum):
    '''
    :stability: experimental
    '''

    V1BETA = "V1BETA"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4ConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={"key": "key", "name": "name", "o_auth": "oAuth"},
)
class GoogleAnalytics4ConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        o_auth: typing.Union["GoogleAnalytics4OAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = GoogleAnalytics4OAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9419ec87b9bd134e1c70777a9c8da70e653d9e3084a51d4a663a2983ee6b37e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def o_auth(self) -> "GoogleAnalytics4OAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("GoogleAnalytics4OAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAnalytics4ConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4OAuthEndpoints",
    jsii_struct_bases=[],
    name_mapping={"authorization": "authorization", "token": "token"},
)
class GoogleAnalytics4OAuthEndpoints:
    def __init__(
        self,
        *,
        authorization: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Google's OAuth token and authorization endpoints.

        :param authorization: (experimental) The OAuth authorization endpoint URI.
        :param token: (experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f20189cf55481a97cb670d9b726f9d5a6fba015c9a9cc896b7e7e6ef2155596c)
            check_type(argname="argument authorization", value=authorization, expected_type=type_hints["authorization"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if authorization is not None:
            self._values["authorization"] = authorization
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def authorization(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth authorization endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("authorization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAnalytics4OAuthEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4OAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class GoogleAnalytics4OAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["GoogleAnalytics4RefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Represents the OAuth flow enabled for the GA4.

        :param refresh_token_grant: (experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = GoogleAnalytics4RefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d54d73d6d3c4814064b63102986f2535facdab1881fee4dc004e8e000da17f0)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "GoogleAnalytics4RefreshTokenGrantFlow":
        '''(experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("GoogleAnalytics4RefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAnalytics4OAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4OAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "endpoints": "endpoints",
        "flow": "flow",
    },
)
class GoogleAnalytics4OAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        endpoints: typing.Optional[typing.Union[GoogleAnalytics4OAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
        flow: typing.Optional[typing.Union[GoogleAnalytics4OAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: (experimental) The access token to be used when interacting with Google Analytics 4. Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired Default: Retrieves a fresh accessToken with the information in the [flow property]{@link GoogleAnalytics4OAuthSettings#flow }
        :param endpoints: (experimental) The OAuth token and authorization endpoints.
        :param flow: (experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired. Default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = GoogleAnalytics4OAuthEndpoints(**endpoints)
        if isinstance(flow, dict):
            flow = GoogleAnalytics4OAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06303ef850b9e990f6fbb8ec4f2680f84193f23b51ccd77d204866d334de5556)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The access token to be used when interacting with Google Analytics 4.

        Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired

        :default: Retrieves a fresh accessToken with the information in the [flow property]{@link GoogleAnalytics4OAuthSettings#flow }

        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def endpoints(self) -> typing.Optional[GoogleAnalytics4OAuthEndpoints]:
        '''(experimental) The OAuth token and authorization endpoints.

        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[GoogleAnalytics4OAuthEndpoints], result)

    @builtins.property
    def flow(self) -> typing.Optional[GoogleAnalytics4OAuthFlow]:
        '''(experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired.

        :default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[GoogleAnalytics4OAuthFlow], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAnalytics4OAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4RefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class GoogleAnalytics4RefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''(experimental) The OAuth elements required for the execution of the refresh token grant flow.

        :param client_id: (experimental) The id of the client app.
        :param client_secret: (experimental) The secret of the client app.
        :param refresh_token: (experimental) A non-expired refresh token.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b8e5ad0344be660e939d8a9049f9e13319ccda543597d267f4807f2faf5b06)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The id of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The secret of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) A non-expired refresh token.

        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAnalytics4RefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4SourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class GoogleAnalytics4SourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: "GoogleAnalytics4ConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Google Analytics v4 Source.

        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c45b3cba2dab0afc04a8bb5504b43b124885419b0f8887d13343dfacf973ce7b)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "GoogleAnalytics4ConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("GoogleAnalytics4ConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleAnalytics4SourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryApiVersion")
class GoogleBigQueryApiVersion(enum.Enum):
    '''
    :stability: experimental
    '''

    V2 = "V2"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={"key": "key", "name": "name", "o_auth": "oAuth"},
)
class GoogleBigQueryConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        o_auth: typing.Union["GoogleBigQueryOAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = GoogleBigQueryOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9973981517794de47b47c46a3990f4a143a2d783edad508f2569fd9a5b0b098)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def o_auth(self) -> "GoogleBigQueryOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("GoogleBigQueryOAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleBigQueryConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryOAuthEndpoints",
    jsii_struct_bases=[],
    name_mapping={"authorization": "authorization", "token": "token"},
)
class GoogleBigQueryOAuthEndpoints:
    def __init__(
        self,
        *,
        authorization: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Google's OAuth token and authorization endpoints.

        :param authorization: (experimental) The OAuth authorization endpoint URI.
        :param token: (experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd41b074442abbb69d9223775ef74cb136d886ea3f758594faff0f12201e9a62)
            check_type(argname="argument authorization", value=authorization, expected_type=type_hints["authorization"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if authorization is not None:
            self._values["authorization"] = authorization
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def authorization(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth authorization endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("authorization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleBigQueryOAuthEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryOAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class GoogleBigQueryOAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["GoogleBigQueryRefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Represents the OAuth flow enabled for the GA4.

        :param refresh_token_grant: (experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = GoogleBigQueryRefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0ab06480e05444b0c04d4f3ef31da672c87ce88f0f25514058ba7f53135a6ad)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "GoogleBigQueryRefreshTokenGrantFlow":
        '''(experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("GoogleBigQueryRefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleBigQueryOAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "endpoints": "endpoints",
        "flow": "flow",
    },
)
class GoogleBigQueryOAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        endpoints: typing.Optional[typing.Union[GoogleBigQueryOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
        flow: typing.Optional[typing.Union[GoogleBigQueryOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: (experimental) The access token to be used when interacting with Google BigQuery. Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired Default: Retrieves a fresh accessToken with the information in the [flow property]{@link GoogleBigQueryOAuthSettings#flow }
        :param endpoints: (experimental) The OAuth token and authorization endpoints.
        :param flow: (experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired. Default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = GoogleBigQueryOAuthEndpoints(**endpoints)
        if isinstance(flow, dict):
            flow = GoogleBigQueryOAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf03c9dd60833d3c00e6be90fc05f6703613db62a4f929a452a11e32ae0aaef)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The access token to be used when interacting with Google BigQuery.

        Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired

        :default: Retrieves a fresh accessToken with the information in the [flow property]{@link GoogleBigQueryOAuthSettings#flow }

        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def endpoints(self) -> typing.Optional[GoogleBigQueryOAuthEndpoints]:
        '''(experimental) The OAuth token and authorization endpoints.

        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[GoogleBigQueryOAuthEndpoints], result)

    @builtins.property
    def flow(self) -> typing.Optional[GoogleBigQueryOAuthFlow]:
        '''(experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired.

        :default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[GoogleBigQueryOAuthFlow], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleBigQueryOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryObject",
    jsii_struct_bases=[],
    name_mapping={"dataset": "dataset", "project": "project", "table": "table"},
)
class GoogleBigQueryObject:
    def __init__(
        self,
        *,
        dataset: builtins.str,
        project: builtins.str,
        table: builtins.str,
    ) -> None:
        '''
        :param dataset: 
        :param project: 
        :param table: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57d63574920e91b25ab7e6df19971d28d83212f260491db85c1e77043b0ae960)
            check_type(argname="argument dataset", value=dataset, expected_type=type_hints["dataset"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dataset": dataset,
            "project": project,
            "table": table,
        }

    @builtins.property
    def dataset(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("dataset")
        assert result is not None, "Required property 'dataset' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleBigQueryObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryRefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class GoogleBigQueryRefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''(experimental) The OAuth elements required for the execution of the refresh token grant flow.

        :param client_id: (experimental) The id of the client app.
        :param client_secret: (experimental) The secret of the client app.
        :param refresh_token: (experimental) A non-expired refresh token.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d458fb271e77d6da1d2f7a891d0b7218ff53a799bd4a2b42faf3639ca6026884)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The id of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The secret of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) A non-expired refresh token.

        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleBigQueryRefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQuerySourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class GoogleBigQuerySourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: typing.Union[GoogleBigQueryObject, typing.Dict[builtins.str, typing.Any]],
        profile: "GoogleBigQueryConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Google BigQuery Source.

        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if isinstance(object, dict):
            object = GoogleBigQueryObject(**object)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c40b8b595c94a8303138555bda9ad1b6d0ca076bb454205adc14900d796a4f6)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> GoogleBigQueryObject:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(GoogleBigQueryObject, result)

    @builtins.property
    def profile(self) -> "GoogleBigQueryConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("GoogleBigQueryConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GoogleBigQuerySourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.HubSpotApiVersion")
class HubSpotApiVersion(enum.Enum):
    '''
    :stability: experimental
    '''

    V1 = "V1"
    '''
    :stability: experimental
    '''
    V2 = "V2"
    '''
    :stability: experimental
    '''
    V3 = "V3"
    '''
    :stability: experimental
    '''
    V4 = "V4"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.HubSpotConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={"key": "key", "name": "name", "o_auth": "oAuth"},
)
class HubSpotConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        o_auth: typing.Union["HubSpotOAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = HubSpotOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2b51399bcb1bd54cdcdd3807c32527ae282f22f4bebe80fa302e196f0c5d962)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def o_auth(self) -> "HubSpotOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("HubSpotOAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubSpotConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.HubSpotDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "entity": "entity",
        "operation": "operation",
        "profile": "profile",
        "error_handling": "errorHandling",
    },
)
class HubSpotDestinationProps:
    def __init__(
        self,
        *,
        api_version: HubSpotApiVersion,
        entity: typing.Sequence[builtins.str],
        operation: "WriteOperation",
        profile: "HubSpotConnectorProfile",
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_version: 
        :param entity: 
        :param operation: 
        :param profile: 
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the HubSpot destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        if isinstance(error_handling, dict):
            error_handling = ErrorHandlingConfiguration(**error_handling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e671cee81f81b7b10893de67ae0fbff6fcce91ee33cd8b966a708e5a963434e)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument entity", value=entity, expected_type=type_hints["entity"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument error_handling", value=error_handling, expected_type=type_hints["error_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "entity": entity,
            "operation": operation,
            "profile": profile,
        }
        if error_handling is not None:
            self._values["error_handling"] = error_handling

    @builtins.property
    def api_version(self) -> HubSpotApiVersion:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(HubSpotApiVersion, result)

    @builtins.property
    def entity(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("entity")
        assert result is not None, "Required property 'entity' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def operation(self) -> "WriteOperation":
        '''
        :stability: experimental
        '''
        result = self._values.get("operation")
        assert result is not None, "Required property 'operation' is missing"
        return typing.cast("WriteOperation", result)

    @builtins.property
    def profile(self) -> "HubSpotConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("HubSpotConnectorProfile", result)

    @builtins.property
    def error_handling(self) -> typing.Optional[ErrorHandlingConfiguration]:
        '''(experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the HubSpot destination.

        For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        result = self._values.get("error_handling")
        return typing.cast(typing.Optional[ErrorHandlingConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubSpotDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.HubSpotOAuthEndpoints",
    jsii_struct_bases=[],
    name_mapping={"token": "token"},
)
class HubSpotOAuthEndpoints:
    def __init__(self, *, token: typing.Optional[builtins.str] = None) -> None:
        '''(experimental) Hubspot OAuth token and authorization endpoints.

        :param token: (experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04cf8bba21518e1c7a3dbacf9d1b594b4eebe6a28dc327c78f6c51e31d96c1dc)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''(experimental) The OAuth token endpoint URI.

        :stability: experimental
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubSpotOAuthEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.HubSpotOAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class HubSpotOAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["HubSpotRefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''(experimental) Represents the OAuth flow enabled for the GA4.

        :param refresh_token_grant: (experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = HubSpotRefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5251656d671e38b2bb0a04996caf851695251d1aebee10fc76744e6d74cda30f)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "HubSpotRefreshTokenGrantFlow":
        '''(experimental) The details required for executing the refresh token grant flow.

        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("HubSpotRefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubSpotOAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.HubSpotOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "endpoints": "endpoints",
        "flow": "flow",
    },
)
class HubSpotOAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        endpoints: typing.Optional[typing.Union[HubSpotOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
        flow: typing.Optional[typing.Union[HubSpotOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: (experimental) The access token to be used when interacting with Hubspot. Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired Default: Retrieves a fresh accessToken with the information in the [flow property]{@link HubSpotOAuthSettings#flow }
        :param endpoints: (experimental) The OAuth token and authorization endpoints.
        :param flow: (experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired. Default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = HubSpotOAuthEndpoints(**endpoints)
        if isinstance(flow, dict):
            flow = HubSpotOAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8731360eb4aae4d089d40080325bf59c21afd86e27a7daf8e5b25402ba927f)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The access token to be used when interacting with Hubspot.

        Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired

        :default: Retrieves a fresh accessToken with the information in the [flow property]{@link HubSpotOAuthSettings#flow }

        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def endpoints(self) -> typing.Optional[HubSpotOAuthEndpoints]:
        '''(experimental) The OAuth token and authorization endpoints.

        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[HubSpotOAuthEndpoints], result)

    @builtins.property
    def flow(self) -> typing.Optional[HubSpotOAuthFlow]:
        '''(experimental) The OAuth flow used for obtaining a new accessToken when the old is not present or expired.

        :default: undefined. AppFlow will not request any new accessToken after expiry.

        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[HubSpotOAuthFlow], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubSpotOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.HubSpotRefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class HubSpotRefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''(experimental) The OAuth elements required for the execution of the refresh token grant flow.

        :param client_id: (experimental) The id of the client app.
        :param client_secret: (experimental) The secret of the client app.
        :param refresh_token: (experimental) A non-expired refresh token.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b942055ffb6eb0b2f2b86333bb1c5fba057ff8ceecb37111500f6f8bb50edda9)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The id of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The secret of the client app.

        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) A non-expired refresh token.

        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubSpotRefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.HubSpotSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "entity": "entity",
        "profile": "profile",
    },
)
class HubSpotSourceProps:
    def __init__(
        self,
        *,
        api_version: HubSpotApiVersion,
        entity: typing.Sequence[builtins.str],
        profile: "HubSpotConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Hubspot Source.

        :param api_version: 
        :param entity: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34a560d5de39bbeb6a291b1135b0a32fdc42fbac6b2ed38ed29582e611f8c0d1)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument entity", value=entity, expected_type=type_hints["entity"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "entity": entity,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> HubSpotApiVersion:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(HubSpotApiVersion, result)

    @builtins.property
    def entity(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("entity")
        assert result is not None, "Required property 'entity' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def profile(self) -> "HubSpotConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("HubSpotConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HubSpotSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IConnectorProfile")
class IConnectorProfile(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''
        :stability: experimental
        '''
        ...


class _IConnectorProfileProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IConnectorProfile"

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "credentials"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IConnectorProfile).__jsii_proxy_class__ = lambda : _IConnectorProfileProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IFlow")
class IFlow(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''
    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the flow.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> FlowType:
        '''(experimental) The type of the flow.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricFlowExecutionRecordsProcessed")
    def metric_flow_execution_records_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of records that Amazon AppFlow attempted to transfer for the flow run.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricFlowExecutionsFailed")
    def metric_flow_executions_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of failed flow runs.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricFlowExecutionsStarted")
    def metric_flow_executions_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of flow runs started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricFlowExecutionsSucceeded")
    def metric_flow_executions_succeeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of successful flow runs.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricFlowExecutionTime")
    def metric_flow_execution_time(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the  interval, in milliseconds, between the time the flow starts and the time it finishes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onRunCompleted")
    def on_run_completed(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="onRunStarted")
    def on_run_started(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        ...


class _IFlowProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''
    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IFlow"

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> FlowType:
        '''(experimental) The type of the flow.

        :stability: experimental
        '''
        return typing.cast(FlowType, jsii.get(self, "type"))

    @jsii.member(jsii_name="metricFlowExecutionRecordsProcessed")
    def metric_flow_execution_records_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of records that Amazon AppFlow attempted to transfer for the flow run.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionRecordsProcessed", [options]))

    @jsii.member(jsii_name="metricFlowExecutionsFailed")
    def metric_flow_executions_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of failed flow runs.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionsFailed", [options]))

    @jsii.member(jsii_name="metricFlowExecutionsStarted")
    def metric_flow_executions_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of flow runs started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionsStarted", [options]))

    @jsii.member(jsii_name="metricFlowExecutionsSucceeded")
    def metric_flow_executions_succeeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of successful flow runs.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionsSucceeded", [options]))

    @jsii.member(jsii_name="metricFlowExecutionTime")
    def metric_flow_execution_time(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the  interval, in milliseconds, between the time the flow starts and the time it finishes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionTime", [options]))

    @jsii.member(jsii_name="onRunCompleted")
    def on_run_completed(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5552b7c97b017064cac75bd8f5d204e42ae9b7d420e7354699555396ba508e0)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onRunCompleted", [id, options]))

    @jsii.member(jsii_name="onRunStarted")
    def on_run_started(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08eabe4de6637500e424a8cdc75ccfceca6fbf225a1b42b189ff54b7c6ead630)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onRunStarted", [id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFlow).__jsii_proxy_class__ = lambda : _IFlowProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IOperation")
class IOperation(typing_extensions.Protocol):
    '''(experimental) A representation of a set of tasks that deliver complete operation.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
        source: "ISource",
    ) -> typing.List[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty]:
        '''
        :param flow: -
        :param source: -

        :stability: experimental
        '''
        ...


class _IOperationProxy:
    '''(experimental) A representation of a set of tasks that deliver complete operation.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IOperation"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
        source: "ISource",
    ) -> typing.List[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty]:
        '''
        :param flow: -
        :param source: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61c118209611ea60b7b0e5493b5cda2a16a36ee38e5f176b7e941ce7afe08468)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        return typing.cast(typing.List[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty], jsii.invoke(self, "bind", [flow, source]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOperation).__jsii_proxy_class__ = lambda : _IOperationProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.ITask")
class ITask(typing_extensions.Protocol):
    '''(experimental) A representation of a unitary action on the record fields.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
        source: "ISource",
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty:
        '''
        :param flow: -
        :param source: -

        :stability: experimental
        '''
        ...


class _ITaskProxy:
    '''(experimental) A representation of a unitary action on the record fields.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.ITask"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
        source: "ISource",
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty:
        '''
        :param flow: -
        :param source: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b48af4a3da83426a2d0417ec6a9087adfdb2f12303453f044e67f619b1a8a52)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty, jsii.invoke(self, "bind", [flow, source]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITask).__jsii_proxy_class__ = lambda : _ITaskProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.ITransform")
class ITransform(IOperation, typing_extensions.Protocol):
    '''(experimental) A representation of a transform operation, that is an operation modifying source fields.

    :stability: experimental
    '''

    pass


class _ITransformProxy(
    jsii.proxy_for(IOperation), # type: ignore[misc]
):
    '''(experimental) A representation of a transform operation, that is an operation modifying source fields.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.ITransform"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITransform).__jsii_proxy_class__ = lambda : _ITransformProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IValidation")
class IValidation(IOperation, typing_extensions.Protocol):
    '''(experimental) A representation of a validation operation, that is an operation testing records and acting on the test results.

    :stability: experimental
    '''

    pass


class _IValidationProxy(
    jsii.proxy_for(IOperation), # type: ignore[misc]
):
    '''(experimental) A representation of a validation operation, that is an operation testing records and acting on the test results.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IValidation"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IValidation).__jsii_proxy_class__ = lambda : _IValidationProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IVertex")
class IVertex(typing_extensions.Protocol):
    '''(experimental) An interface representing a vertex, i.e. a source or a destination of an AppFlow flow.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        ...


class _IVertexProxy:
    '''(experimental) An interface representing a vertex, i.e. a source or a destination of an AppFlow flow.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IVertex"

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IVertex).__jsii_proxy_class__ = lambda : _IVertexProxy


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.JdbcDriver")
class JdbcDriver(enum.Enum):
    '''
    :stability: experimental
    '''

    POSTGRES = "POSTGRES"
    '''
    :stability: experimental
    '''
    MYSQL = "MYSQL"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.JdbcSmallDataScaleBasicAuthSettings",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class JdbcSmallDataScaleBasicAuthSettings:
    def __init__(
        self,
        *,
        password: _aws_cdk_ceddda9d.SecretValue,
        username: builtins.str,
    ) -> None:
        '''(experimental) Basic authentication settings for the JdbcSmallDataScaleConnectorProfile.

        :param password: (experimental) The password of the identity used for interacting with the database.
        :param username: (experimental) The username of the identity used for interacting with the database.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb0c6a784d526fe673880a8dc8853f501be865bacf284293ad9648077787b15f)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''(experimental) The password of the identity used for interacting with the database.

        :stability: experimental
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''(experimental) The username of the identity used for interacting with the database.

        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JdbcSmallDataScaleBasicAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.JdbcSmallDataScaleConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "basic_auth": "basicAuth",
        "database": "database",
        "driver": "driver",
        "hostname": "hostname",
        "port": "port",
    },
)
class JdbcSmallDataScaleConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        basic_auth: typing.Union[JdbcSmallDataScaleBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
        database: builtins.str,
        driver: JdbcDriver,
        hostname: builtins.str,
        port: jsii.Number,
    ) -> None:
        '''(experimental) Properties for the JdbcSmallDataScaleConnectorProfile.

        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param basic_auth: (experimental) The auth settings for the profile.
        :param database: (experimental) The name of the database.
        :param driver: (experimental) The driver for the database. Effectively specifies the type of database.
        :param hostname: (experimental) The hostname of the database to interact with.
        :param port: (experimental) The database communication port.

        :stability: experimental
        '''
        if isinstance(basic_auth, dict):
            basic_auth = JdbcSmallDataScaleBasicAuthSettings(**basic_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc14393bb8b8efbaa54178e594c59963d49e2b229727f448ac8fb291bbeb4995)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument driver", value=driver, expected_type=type_hints["driver"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "basic_auth": basic_auth,
            "database": database,
            "driver": driver,
            "hostname": hostname,
            "port": port,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def basic_auth(self) -> JdbcSmallDataScaleBasicAuthSettings:
        '''(experimental) The auth settings for the profile.

        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        assert result is not None, "Required property 'basic_auth' is missing"
        return typing.cast(JdbcSmallDataScaleBasicAuthSettings, result)

    @builtins.property
    def database(self) -> builtins.str:
        '''(experimental) The name of the database.

        :stability: experimental
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def driver(self) -> JdbcDriver:
        '''(experimental) The driver for the database.

        Effectively specifies the type of database.

        :stability: experimental
        '''
        result = self._values.get("driver")
        assert result is not None, "Required property 'driver' is missing"
        return typing.cast(JdbcDriver, result)

    @builtins.property
    def hostname(self) -> builtins.str:
        '''(experimental) The hostname of the database to interact with.

        :stability: experimental
        '''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> jsii.Number:
        '''(experimental) The database communication port.

        :stability: experimental
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JdbcSmallDataScaleConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.JdbcSmallDataScaleObject",
    jsii_struct_bases=[],
    name_mapping={"schema": "schema", "table": "table"},
)
class JdbcSmallDataScaleObject:
    def __init__(self, *, schema: builtins.str, table: builtins.str) -> None:
        '''
        :param schema: 
        :param table: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e934abcd418f8a3346c0203b271d64a00de231c61d22b48d24e0c25a67b404e1)
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "schema": schema,
            "table": table,
        }

    @builtins.property
    def schema(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("schema")
        assert result is not None, "Required property 'schema' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def table(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JdbcSmallDataScaleObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.JdbcSmallDataScaleSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "api_version": "apiVersion",
    },
)
class JdbcSmallDataScaleSourceProps:
    def __init__(
        self,
        *,
        object: typing.Union[JdbcSmallDataScaleObject, typing.Dict[builtins.str, typing.Any]],
        profile: "JdbcSmallDataScaleConnectorProfile",
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        if isinstance(object, dict):
            object = JdbcSmallDataScaleObject(**object)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58c61c2bd9e826806d9e1a1c701fc3b78eb7b197b458672bd695b12d578c5093)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if api_version is not None:
            self._values["api_version"] = api_version

    @builtins.property
    def object(self) -> JdbcSmallDataScaleObject:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(JdbcSmallDataScaleObject, result)

    @builtins.property
    def profile(self) -> "JdbcSmallDataScaleConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("JdbcSmallDataScaleConnectorProfile", result)

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "JdbcSmallDataScaleSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.MailchimpApiVersion")
class MailchimpApiVersion(enum.Enum):
    '''(experimental) An enum representing the Mailchimp API versions.

    :stability: experimental
    '''

    V3 = "V3"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MailchimpConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "api_key": "apiKey",
        "instance_url": "instanceUrl",
    },
)
class MailchimpConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        api_key: _aws_cdk_ceddda9d.SecretValue,
        instance_url: builtins.str,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param api_key: 
        :param instance_url: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01619582f0540dc2247df97a632e56a45484d0e100a27d38e67e6ee1bf631032)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_key": api_key,
            "instance_url": instance_url,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_key")
        assert result is not None, "Required property 'api_key' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MailchimpConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MailchimpSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class MailchimpSourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: "MailchimpConnectorProfile",
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__997ea399b9fcc0497f84b977ed8f1cea34402f74de270398f7fab9b7ae8e7cf6)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "MailchimpConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("MailchimpConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MailchimpSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MapAllConfig",
    jsii_struct_bases=[],
    name_mapping={"exclude": "exclude"},
)
class MapAllConfig:
    def __init__(self, *, exclude: typing.Sequence[builtins.str]) -> None:
        '''(experimental) A helper interface.

        :param exclude: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82007c94804b84589edff57bc8718212e6520637e6aa1a5e7f2cf7d6c731140a)
            check_type(argname="argument exclude", value=exclude, expected_type=type_hints["exclude"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "exclude": exclude,
        }

    @builtins.property
    def exclude(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("exclude")
        assert result is not None, "Required property 'exclude' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MapAllConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MarketoConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "instance_url": "instanceUrl",
        "o_auth": "oAuth",
    },
)
class MarketoConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        instance_url: builtins.str,
        o_auth: typing.Union["MarketoOAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param instance_url: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = MarketoOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56518be30567e8057ee44cb46e6f916ae9f0c67fdb4fcd0b3f2e5eda69b2313e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_url": instance_url,
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def o_auth(self) -> "MarketoOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("MarketoOAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MarketoConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MarketoInstanceUrlBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MarketoInstanceUrlBuilder",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildFromAccount")
    @builtins.classmethod
    def build_from_account(cls, account: builtins.str) -> builtins.str:
        '''
        :param account: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__801380782fb1f9681b6e6f5423656cf05c94ef570d51daa36920d39b1c56057f)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "buildFromAccount", [account]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MarketoOAuthClientCredentialsFlow",
    jsii_struct_bases=[],
    name_mapping={"client_id": "clientId", "client_secret": "clientSecret"},
)
class MarketoOAuthClientCredentialsFlow:
    def __init__(
        self,
        *,
        client_id: _aws_cdk_ceddda9d.SecretValue,
        client_secret: _aws_cdk_ceddda9d.SecretValue,
    ) -> None:
        '''
        :param client_id: 
        :param client_secret: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64a0405859705dce311d70baebb3bc505d535da9b60e5fdba7a7304025592485)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_id": client_id,
            "client_secret": client_secret,
        }

    @builtins.property
    def client_id(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def client_secret(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MarketoOAuthClientCredentialsFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MarketoOAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"client_credentials": "clientCredentials"},
)
class MarketoOAuthFlow:
    def __init__(
        self,
        *,
        client_credentials: typing.Union[MarketoOAuthClientCredentialsFlow, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param client_credentials: 

        :stability: experimental
        '''
        if isinstance(client_credentials, dict):
            client_credentials = MarketoOAuthClientCredentialsFlow(**client_credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d600bcb42bd2309d8a211399acb48b622ca7b46af03035c5555e3747e2ef2b59)
            check_type(argname="argument client_credentials", value=client_credentials, expected_type=type_hints["client_credentials"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_credentials": client_credentials,
        }

    @builtins.property
    def client_credentials(self) -> MarketoOAuthClientCredentialsFlow:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_credentials")
        assert result is not None, "Required property 'client_credentials' is missing"
        return typing.cast(MarketoOAuthClientCredentialsFlow, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MarketoOAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MarketoOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={"flow": "flow", "access_token": "accessToken"},
)
class MarketoOAuthSettings:
    def __init__(
        self,
        *,
        flow: typing.Union[MarketoOAuthFlow, typing.Dict[builtins.str, typing.Any]],
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param flow: 
        :param access_token: 

        :stability: experimental
        '''
        if isinstance(flow, dict):
            flow = MarketoOAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86263784684ceb950a00a13766dde95f979dfffada2529e1c69eb58d4b6c85cf)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "flow": flow,
        }
        if access_token is not None:
            self._values["access_token"] = access_token

    @builtins.property
    def flow(self) -> MarketoOAuthFlow:
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        assert result is not None, "Required property 'flow' is missing"
        return typing.cast(MarketoOAuthFlow, result)

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MarketoOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MarketoSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "api_version": "apiVersion",
    },
)
class MarketoSourceProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        profile: "MarketoConnectorProfile",
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeb8aa31cd135e4c5ed673ca30e70e83e3cd86d41801f9699ebb510885b962c9)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if api_version is not None:
            self._values["api_version"] = api_version

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "MarketoConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("MarketoConnectorProfile", result)

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MarketoSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MicrosoftDynamics365ApiUrlBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365ApiUrlBuilder",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildApiUrl")
    @builtins.classmethod
    def build_api_url(cls, org: builtins.str) -> builtins.str:
        '''
        :param org: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1379032787009926181873ccc305a0955e2dd0d58473a4e17ec4430f0821186)
            check_type(argname="argument org", value=org, expected_type=type_hints["org"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "buildApiUrl", [org]))


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365ApiVersion")
class MicrosoftDynamics365ApiVersion(enum.Enum):
    '''(experimental) An enum representing the Microsoft Dynamics 365 API versions.

    :stability: experimental
    '''

    V9_2 = "V9_2"
    '''(experimental) Version 9.2.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365ConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "instance_url": "instanceUrl",
        "o_auth": "oAuth",
    },
)
class MicrosoftDynamics365ConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        instance_url: builtins.str,
        o_auth: typing.Union["MicrosoftDynamics365OAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param instance_url: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = MicrosoftDynamics365OAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__011f223bbcc29a271af1ee4b50f8ca7ad6193b80b57bb4bf79ab8908466f4f6f)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_url": instance_url,
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def o_auth(self) -> "MicrosoftDynamics365OAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("MicrosoftDynamics365OAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftDynamics365ConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365OAuthEndpointsSettings",
    jsii_struct_bases=[],
    name_mapping={"token": "token"},
)
class MicrosoftDynamics365OAuthEndpointsSettings:
    def __init__(self, *, token: builtins.str) -> None:
        '''
        :param token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8268da092369f76bea8d817f9a7cc1d8dcbd2cecd8bc62823c2b8a09e5138ecf)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token": token,
        }

    @builtins.property
    def token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftDynamics365OAuthEndpointsSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365OAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class MicrosoftDynamics365OAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["MicrosoftDynamics365RefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param refresh_token_grant: 

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = MicrosoftDynamics365RefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93211fb9a48d02c2fdab04e73373bab19f2d26fa185f83be7274e93c2e19e291)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "MicrosoftDynamics365RefreshTokenGrantFlow":
        '''
        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("MicrosoftDynamics365RefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftDynamics365OAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365OAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "endpoints": "endpoints",
        "flow": "flow",
    },
)
class MicrosoftDynamics365OAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        endpoints: typing.Optional[typing.Union[MicrosoftDynamics365OAuthEndpointsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        flow: typing.Optional[typing.Union[MicrosoftDynamics365OAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: (experimental) The access token to be used when interacting with Microsoft Dynamics 365. Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired
        :param endpoints: 
        :param flow: 

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = MicrosoftDynamics365OAuthEndpointsSettings(**endpoints)
        if isinstance(flow, dict):
            flow = MicrosoftDynamics365OAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70b43b0200fa65d2295e51564572c42fc602eafb615e50fe451764dc9b3dc0dc)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The access token to be used when interacting with Microsoft Dynamics 365.

        Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired

        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def endpoints(self) -> typing.Optional[MicrosoftDynamics365OAuthEndpointsSettings]:
        '''
        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[MicrosoftDynamics365OAuthEndpointsSettings], result)

    @builtins.property
    def flow(self) -> typing.Optional[MicrosoftDynamics365OAuthFlow]:
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[MicrosoftDynamics365OAuthFlow], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftDynamics365OAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365RefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class MicrosoftDynamics365RefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param client_id: 
        :param client_secret: 
        :param refresh_token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ae109d309d44a0e101cf414fca29def31504e79769a613872554b0a0d2b6fb7)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftDynamics365RefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365SourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class MicrosoftDynamics365SourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: "MicrosoftDynamics365ConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Microsoft Dynamics 365 Source.

        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0e2926195df1e6dde7926b4f3ae2791126310b2c1e58f11485f1bc89e44f721)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "MicrosoftDynamics365ConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("MicrosoftDynamics365ConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftDynamics365SourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MicrosoftDynamics365TokenUrlBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365TokenUrlBuilder",
):
    '''(experimental) A utility class for building Microsoft Dynamics 365 token URLs.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildTokenUrl")
    @builtins.classmethod
    def build_token_url(
        cls,
        tenant_id: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''
        :param tenant_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0daf40ee42977120a5d3bc0ed71c20baf74dac7c3610abf7105cdc27386d8f02)
            check_type(argname="argument tenant_id", value=tenant_id, expected_type=type_hints["tenant_id"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "buildTokenUrl", [tenant_id]))


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineApiVersion")
class MicrosoftSharepointOnlineApiVersion(enum.Enum):
    '''(experimental) An enum representing the Microsoft Sharepoint Online API versions.

    :stability: experimental
    '''

    V1 = "V1"
    '''(experimental) Version 1.0.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={"key": "key", "name": "name", "o_auth": "oAuth"},
)
class MicrosoftSharepointOnlineConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        o_auth: typing.Union["MicrosoftSharepointOnlineOAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = MicrosoftSharepointOnlineOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d26b7adf0fd56806c77413a8c33710b15aa17f977d91a0b02c4bfad24d438388)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def o_auth(self) -> "MicrosoftSharepointOnlineOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("MicrosoftSharepointOnlineOAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftSharepointOnlineConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineOAuthEndpointsSettings",
    jsii_struct_bases=[],
    name_mapping={"token": "token"},
)
class MicrosoftSharepointOnlineOAuthEndpointsSettings:
    def __init__(self, *, token: builtins.str) -> None:
        '''
        :param token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c44499b6b9db0006d3bd2b6d0016f0323662a961adc66eba56a2a83de73dc880)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token": token,
        }

    @builtins.property
    def token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftSharepointOnlineOAuthEndpointsSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineOAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class MicrosoftSharepointOnlineOAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["MicrosoftSharepointOnlineRefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param refresh_token_grant: 

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = MicrosoftSharepointOnlineRefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17dc0229e5b64936d4f7654c81ea06d1085aecfb20d954aa8ecfde4abe614d72)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "MicrosoftSharepointOnlineRefreshTokenGrantFlow":
        '''
        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("MicrosoftSharepointOnlineRefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftSharepointOnlineOAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "endpoints": "endpoints",
        "flow": "flow",
    },
)
class MicrosoftSharepointOnlineOAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        endpoints: typing.Optional[typing.Union[MicrosoftSharepointOnlineOAuthEndpointsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        flow: typing.Optional[typing.Union[MicrosoftSharepointOnlineOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: (experimental) The access token to be used when interacting with Microsoft Sharepoint Online. Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired
        :param endpoints: 
        :param flow: 

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = MicrosoftSharepointOnlineOAuthEndpointsSettings(**endpoints)
        if isinstance(flow, dict):
            flow = MicrosoftSharepointOnlineOAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__716e62ba44f6f6a83bf1d88a18cdcf2063d3d613688088456b12654e5e384e2f)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''(experimental) The access token to be used when interacting with Microsoft Sharepoint Online.

        Note that if only the access token is provided AppFlow is not able to retrieve a fresh access token when the current one is expired

        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def endpoints(
        self,
    ) -> typing.Optional[MicrosoftSharepointOnlineOAuthEndpointsSettings]:
        '''
        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[MicrosoftSharepointOnlineOAuthEndpointsSettings], result)

    @builtins.property
    def flow(self) -> typing.Optional[MicrosoftSharepointOnlineOAuthFlow]:
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[MicrosoftSharepointOnlineOAuthFlow], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftSharepointOnlineOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineObject",
    jsii_struct_bases=[],
    name_mapping={"site": "site", "drives": "drives", "entities": "entities"},
)
class MicrosoftSharepointOnlineObject:
    def __init__(
        self,
        *,
        site: builtins.str,
        drives: typing.Optional[typing.Sequence[builtins.str]] = None,
        entities: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Represents a list of Microsoft Sharepoint Online site drives from which to retrieve the documents.

        :param site: (experimental) The Microsoft Sharepoint Online site from which the documents are to be retrieved. Note: requires full name starting with 'sites/'
        :param drives: (deprecated) An array of Microsoft Sharepoint Online site drives from which the documents are to be retrieved. Note: each drive requires full name starting with 'drives/'
        :param entities: (experimental) An array of Microsoft Sharepoint Online site entities from which the documents are to be retrieved. Note: each entity requires full name starting with 'drives/' followed by driveID and optional '/items/' followed by itemID

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a0923fbe091b534d3a1ca8d9ba5097c24ea632b8fd07c4a6c57f8145d43b6ad)
            check_type(argname="argument site", value=site, expected_type=type_hints["site"])
            check_type(argname="argument drives", value=drives, expected_type=type_hints["drives"])
            check_type(argname="argument entities", value=entities, expected_type=type_hints["entities"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "site": site,
        }
        if drives is not None:
            self._values["drives"] = drives
        if entities is not None:
            self._values["entities"] = entities

    @builtins.property
    def site(self) -> builtins.str:
        '''(experimental) The Microsoft Sharepoint Online site from which the documents are to be retrieved.

        Note: requires full name starting with 'sites/'

        :stability: experimental
        '''
        result = self._values.get("site")
        assert result is not None, "Required property 'site' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def drives(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(deprecated) An array of Microsoft Sharepoint Online site drives from which the documents are to be retrieved.

        Note: each drive requires full name starting with 'drives/'

        :deprecated: . This property is deprecated and will be removed in a future release. Use {@link entities } instead

        :stability: deprecated
        '''
        result = self._values.get("drives")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def entities(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) An array of Microsoft Sharepoint Online site entities from which the documents are to be retrieved.

        Note: each entity requires full name starting with 'drives/' followed by driveID and optional '/items/' followed by itemID

        :stability: experimental

        Example::

            "drives/${driveID}/items/${itemID}"
        '''
        result = self._values.get("entities")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftSharepointOnlineObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineRefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class MicrosoftSharepointOnlineRefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param client_id: 
        :param client_secret: 
        :param refresh_token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4a2d0ff5431cb6dd067791d63c4cdafd6c010289443e62713e19daf55335d75)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftSharepointOnlineRefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class MicrosoftSharepointOnlineSourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: typing.Union[MicrosoftSharepointOnlineObject, typing.Dict[builtins.str, typing.Any]],
        profile: "MicrosoftSharepointOnlineConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Microsoft Sharepoint Online Source.

        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if isinstance(object, dict):
            object = MicrosoftSharepointOnlineObject(**object)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c5ba72fb01ff6d8aef9465671d0c5e3f4de630b3ad915e9a96ded987c4eedcd)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> MicrosoftSharepointOnlineObject:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(MicrosoftSharepointOnlineObject, result)

    @builtins.property
    def profile(self) -> "MicrosoftSharepointOnlineConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("MicrosoftSharepointOnlineConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MicrosoftSharepointOnlineSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MicrosoftSharepointOnlineTokenUrlBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineTokenUrlBuilder",
):
    '''(experimental) A utility class for building Microsoft Online token URLs.

    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildTokenUrl")
    @builtins.classmethod
    def build_token_url(
        cls,
        tenant_id: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''
        :param tenant_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9eea2823b899bd9f32f2a9d6ef72227e8b50a7af088cc1f940d8649c10c830e8)
            check_type(argname="argument tenant_id", value=tenant_id, expected_type=type_hints["tenant_id"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "buildTokenUrl", [tenant_id]))


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.OAuth2GrantType")
class OAuth2GrantType(enum.Enum):
    '''
    :stability: experimental
    '''

    CLIENT_CREDENTIALS = "CLIENT_CREDENTIALS"
    '''
    :stability: experimental
    '''
    AUTHORIZATION_CODE = "AUTHORIZATION_CODE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.OnDemandFlowProps",
    jsii_struct_bases=[FlowProps],
    name_mapping={
        "destination": "destination",
        "mappings": "mappings",
        "source": "source",
        "description": "description",
        "filters": "filters",
        "key": "key",
        "name": "name",
        "transforms": "transforms",
        "validations": "validations",
    },
)
class OnDemandFlowProps(FlowProps):
    def __init__(
        self,
        *,
        destination: "IDestination",
        mappings: typing.Sequence["IMapping"],
        source: "ISource",
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence["IFilter"]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
    ) -> None:
        '''
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a637938864a788d69acdfb22629eb81f7a59bfd0ae6a54ea8850a8c2452e7086)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument transforms", value=transforms, expected_type=type_hints["transforms"])
            check_type(argname="argument validations", value=validations, expected_type=type_hints["validations"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
            "mappings": mappings,
            "source": source,
        }
        if description is not None:
            self._values["description"] = description
        if filters is not None:
            self._values["filters"] = filters
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if transforms is not None:
            self._values["transforms"] = transforms
        if validations is not None:
            self._values["validations"] = validations

    @builtins.property
    def destination(self) -> "IDestination":
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("IDestination", result)

    @builtins.property
    def mappings(self) -> typing.List["IMapping"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List["IMapping"], result)

    @builtins.property
    def source(self) -> "ISource":
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("ISource", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List["IFilter"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List["IFilter"]], result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transforms(self) -> typing.Optional[typing.List[ITransform]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("transforms")
        return typing.cast(typing.Optional[typing.List[ITransform]], result)

    @builtins.property
    def validations(self) -> typing.Optional[typing.List[IValidation]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("validations")
        return typing.cast(typing.Optional[typing.List[IValidation]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnDemandFlowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IOperation)
class OperationBase(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-appflow.OperationBase",
):
    '''(experimental) A base class for all operations.

    :stability: experimental
    '''

    def __init__(self, tasks: typing.Sequence[ITask]) -> None:
        '''
        :param tasks: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9407225e27dbb4838ea7b03f43774d6a10e258ec3db30d4046317f81bc86197a)
            check_type(argname="argument tasks", value=tasks, expected_type=type_hints["tasks"])
        jsii.create(self.__class__, self, [tasks])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
        source: "ISource",
    ) -> typing.List[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty]:
        '''
        :param flow: -
        :param source: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e96aa6ca236dcbbffdd35eba014e3957a264c044051bae3dd2674912fb199e81)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        return typing.cast(typing.List[_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty], jsii.invoke(self, "bind", [flow, source]))


class _OperationBaseProxy(OperationBase):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, OperationBase).__jsii_proxy_class__ = lambda : _OperationBaseProxy


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.RedshiftConnectorBasicCredentials",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class RedshiftConnectorBasicCredentials:
    def __init__(
        self,
        *,
        password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param password: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d0aa93167e776d8c97b0ea87e2dcf46b18ed3f17bee9a998bf24417176cac02)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def password(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftConnectorBasicCredentials(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.RedshiftConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "basic_auth": "basicAuth",
        "cluster": "cluster",
        "database_name": "databaseName",
        "intermediate_location": "intermediateLocation",
        "bucket_access_role": "bucketAccessRole",
        "data_api_role": "dataApiRole",
    },
)
class RedshiftConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        basic_auth: typing.Union[RedshiftConnectorBasicCredentials, typing.Dict[builtins.str, typing.Any]],
        cluster: _aws_cdk_aws_redshift_alpha_9727f5af.ICluster,
        database_name: builtins.str,
        intermediate_location: typing.Union["S3Location", typing.Dict[builtins.str, typing.Any]],
        bucket_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        data_api_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param basic_auth: 
        :param cluster: (experimental) The Redshift cluster to use this connector profile with.
        :param database_name: (experimental) The name of the database which the RedshiftConnectorProfile will be working with.
        :param intermediate_location: (experimental) An intermediate location for the data retrieved from the flow source that will be further transferred to the Redshfit database.
        :param bucket_access_role: (experimental) An IAM Role that the Redshift cluster will assume to get data from the intermiediate S3 Bucket.
        :param data_api_role: (experimental) An IAM Role that AppFlow will assume to interact with the Redshift cluster's Data API. Default: autogenerated IAM role

        :stability: experimental
        '''
        if isinstance(basic_auth, dict):
            basic_auth = RedshiftConnectorBasicCredentials(**basic_auth)
        if isinstance(intermediate_location, dict):
            intermediate_location = S3Location(**intermediate_location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d871624f397acc790fe4b2dff61b2c9af47bf80e85930bbc060e18210cf26a0)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument database_name", value=database_name, expected_type=type_hints["database_name"])
            check_type(argname="argument intermediate_location", value=intermediate_location, expected_type=type_hints["intermediate_location"])
            check_type(argname="argument bucket_access_role", value=bucket_access_role, expected_type=type_hints["bucket_access_role"])
            check_type(argname="argument data_api_role", value=data_api_role, expected_type=type_hints["data_api_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "basic_auth": basic_auth,
            "cluster": cluster,
            "database_name": database_name,
            "intermediate_location": intermediate_location,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if bucket_access_role is not None:
            self._values["bucket_access_role"] = bucket_access_role
        if data_api_role is not None:
            self._values["data_api_role"] = data_api_role

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def basic_auth(self) -> RedshiftConnectorBasicCredentials:
        '''
        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        assert result is not None, "Required property 'basic_auth' is missing"
        return typing.cast(RedshiftConnectorBasicCredentials, result)

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_redshift_alpha_9727f5af.ICluster:
        '''(experimental) The Redshift cluster to use this connector profile with.

        :stability: experimental
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_redshift_alpha_9727f5af.ICluster, result)

    @builtins.property
    def database_name(self) -> builtins.str:
        '''(experimental) The name of the database which the RedshiftConnectorProfile will be working with.

        :stability: experimental
        '''
        result = self._values.get("database_name")
        assert result is not None, "Required property 'database_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def intermediate_location(self) -> "S3Location":
        '''(experimental) An intermediate location for the data retrieved from the flow source that will be further transferred to the Redshfit database.

        :stability: experimental
        '''
        result = self._values.get("intermediate_location")
        assert result is not None, "Required property 'intermediate_location' is missing"
        return typing.cast("S3Location", result)

    @builtins.property
    def bucket_access_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM Role that the Redshift cluster will assume to get data from the intermiediate S3 Bucket.

        :stability: experimental
        '''
        result = self._values.get("bucket_access_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def data_api_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM Role that AppFlow will assume to interact with the Redshift cluster's Data API.

        :default: autogenerated IAM role

        :stability: experimental
        '''
        result = self._values.get("data_api_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.RedshiftDestinationObject",
    jsii_struct_bases=[],
    name_mapping={"table": "table", "schema": "schema"},
)
class RedshiftDestinationObject:
    def __init__(
        self,
        *,
        table: typing.Union[builtins.str, _aws_cdk_aws_redshift_alpha_9727f5af.ITable],
        schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param table: 
        :param schema: Default: public

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__023bd631842c0c7e2507f9b94b65983b72d1ca7397b9d0e6eaa671613022e654)
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table": table,
        }
        if schema is not None:
            self._values["schema"] = schema

    @builtins.property
    def table(
        self,
    ) -> typing.Union[builtins.str, _aws_cdk_aws_redshift_alpha_9727f5af.ITable]:
        '''
        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(typing.Union[builtins.str, _aws_cdk_aws_redshift_alpha_9727f5af.ITable], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''
        :default: public

        :stability: experimental
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDestinationObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.RedshiftDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "error_handling": "errorHandling",
    },
)
class RedshiftDestinationProps:
    def __init__(
        self,
        *,
        object: typing.Union[RedshiftDestinationObject, typing.Dict[builtins.str, typing.Any]],
        profile: "RedshiftConnectorProfile",
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param object: (experimental) A Redshift table object (optionally with the schema).
        :param profile: (experimental) An instance of the.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        if isinstance(object, dict):
            object = RedshiftDestinationObject(**object)
        if isinstance(error_handling, dict):
            error_handling = ErrorHandlingConfiguration(**error_handling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26848c0b62c9c9752bc706327fec0a52eb543988fb667720c479490dd72e453c)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument error_handling", value=error_handling, expected_type=type_hints["error_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if error_handling is not None:
            self._values["error_handling"] = error_handling

    @builtins.property
    def object(self) -> RedshiftDestinationObject:
        '''(experimental) A Redshift table object (optionally with the schema).

        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(RedshiftDestinationObject, result)

    @builtins.property
    def profile(self) -> "RedshiftConnectorProfile":
        '''(experimental) An instance of the.

        :stability: experimental
        :type: RedshiftConnectorProfile
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("RedshiftConnectorProfile", result)

    @builtins.property
    def error_handling(self) -> typing.Optional[ErrorHandlingConfiguration]:
        '''(experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination.

        For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        result = self._values.get("error_handling")
        return typing.cast(typing.Optional[ErrorHandlingConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RedshiftDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3Catalog",
    jsii_struct_bases=[],
    name_mapping={
        "database": "database",
        "table_prefix": "tablePrefix",
        "role": "role",
    },
)
class S3Catalog:
    def __init__(
        self,
        *,
        database: _aws_cdk_aws_glue_alpha_ce674d29.IDatabase,
        table_prefix: builtins.str,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    ) -> None:
        '''
        :param database: (experimental) The AWS Glue database that will contain the tables created when the flow executes.
        :param table_prefix: (experimental) The prefix for the tables created in the AWS Glue database.
        :param role: (experimental) The IAM Role that will be used for data catalog operations. Default: - A new role will be created

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bea771096082895a3b2fdb0a6ef285d5a6dcd168c3b1c7817b36f3d94483138)
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument table_prefix", value=table_prefix, expected_type=type_hints["table_prefix"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "database": database,
            "table_prefix": table_prefix,
        }
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def database(self) -> _aws_cdk_aws_glue_alpha_ce674d29.IDatabase:
        '''(experimental) The AWS Glue database that will contain the tables created when the flow executes.

        :stability: experimental
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(_aws_cdk_aws_glue_alpha_ce674d29.IDatabase, result)

    @builtins.property
    def table_prefix(self) -> builtins.str:
        '''(experimental) The prefix for the tables created in the AWS Glue database.

        :stability: experimental
        '''
        result = self._values.get("table_prefix")
        assert result is not None, "Required property 'table_prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM Role that will be used for data catalog operations.

        :default: - A new role will be created

        :stability: experimental
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3Catalog(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3DestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "location": "location",
        "catalog": "catalog",
        "formatting": "formatting",
    },
)
class S3DestinationProps:
    def __init__(
        self,
        *,
        location: typing.Union["S3Location", typing.Dict[builtins.str, typing.Any]],
        catalog: typing.Optional[typing.Union[S3Catalog, typing.Dict[builtins.str, typing.Any]]] = None,
        formatting: typing.Optional[typing.Union["S3OutputFormatting", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param location: (experimental) The S3 location of the files with the retrieved data.
        :param catalog: (experimental) The AWS Glue cataloging options.
        :param formatting: (experimental) The formatting options for the output files.

        :stability: experimental
        '''
        if isinstance(location, dict):
            location = S3Location(**location)
        if isinstance(catalog, dict):
            catalog = S3Catalog(**catalog)
        if isinstance(formatting, dict):
            formatting = S3OutputFormatting(**formatting)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcfab06fa3a7f71b0e7bb0a5d9ad3825206b0dd52d444967bdcb662797fbd338)
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument catalog", value=catalog, expected_type=type_hints["catalog"])
            check_type(argname="argument formatting", value=formatting, expected_type=type_hints["formatting"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "location": location,
        }
        if catalog is not None:
            self._values["catalog"] = catalog
        if formatting is not None:
            self._values["formatting"] = formatting

    @builtins.property
    def location(self) -> "S3Location":
        '''(experimental) The S3 location of the files with the retrieved data.

        :stability: experimental
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast("S3Location", result)

    @builtins.property
    def catalog(self) -> typing.Optional[S3Catalog]:
        '''(experimental) The AWS Glue cataloging options.

        :stability: experimental
        '''
        result = self._values.get("catalog")
        return typing.cast(typing.Optional[S3Catalog], result)

    @builtins.property
    def formatting(self) -> typing.Optional["S3OutputFormatting"]:
        '''(experimental) The formatting options for the output files.

        :stability: experimental
        '''
        result = self._values.get("formatting")
        return typing.cast(typing.Optional["S3OutputFormatting"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3DestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3FileAggregation",
    jsii_struct_bases=[],
    name_mapping={"file_size": "fileSize", "type": "type"},
)
class S3FileAggregation:
    def __init__(
        self,
        *,
        file_size: typing.Optional[jsii.Number] = None,
        type: typing.Optional["S3OutputAggregationType"] = None,
    ) -> None:
        '''
        :param file_size: (experimental) The maximum size, in MB, of the file containing portion of incoming data.
        :param type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a2f9712666e80398c9230f454c7c60b9bae2fac1dbb25be213d6ad5a917f82)
            check_type(argname="argument file_size", value=file_size, expected_type=type_hints["file_size"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if file_size is not None:
            self._values["file_size"] = file_size
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def file_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum size, in MB, of the file containing portion of incoming data.

        :stability: experimental
        '''
        result = self._values.get("file_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional["S3OutputAggregationType"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["S3OutputAggregationType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3FileAggregation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.S3InputFileType")
class S3InputFileType(enum.Enum):
    '''(experimental) The file type that Amazon AppFlow gets from your Amazon S3 bucket.

    :stability: experimental
    '''

    CSV = "CSV"
    '''
    :stability: experimental
    '''
    JSON = "JSON"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3InputFormat",
    jsii_struct_bases=[],
    name_mapping={"type": "type"},
)
class S3InputFormat:
    def __init__(self, *, type: S3InputFileType) -> None:
        '''
        :param type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b6f8b75a73786f0e12a1a707e6c0214b9f2b1718fee0bc1bca7b4ae05c33642)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }

    @builtins.property
    def type(self) -> S3InputFileType:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(S3InputFileType, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3InputFormat(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3Location",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "prefix": "prefix"},
)
class S3Location:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket: 
        :param prefix: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e77dee49c84e2591524d02869bd5c43168a375fb8148cbbc25c2e89cc70ef607)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
        }
        if prefix is not None:
            self._values["prefix"] = prefix

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3Location(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.S3OutputAggregationType")
class S3OutputAggregationType(enum.Enum):
    '''
    :stability: experimental
    '''

    NONE = "NONE"
    '''
    :stability: experimental
    '''
    SINGLE_FILE = "SINGLE_FILE"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3OutputFilePrefix",
    jsii_struct_bases=[],
    name_mapping={"format": "format", "hierarchy": "hierarchy", "type": "type"},
)
class S3OutputFilePrefix:
    def __init__(
        self,
        *,
        format: typing.Optional["S3OutputFilePrefixFormat"] = None,
        hierarchy: typing.Optional[typing.Sequence["S3OutputFilePrefixHierarchy"]] = None,
        type: typing.Optional["S3OutputFilePrefixType"] = None,
    ) -> None:
        '''
        :param format: 
        :param hierarchy: 
        :param type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07222f7ad6e14c07d1c839889d580bf00d9a135a0c0da6a5dc9b6846a66c125f)
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument hierarchy", value=hierarchy, expected_type=type_hints["hierarchy"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if format is not None:
            self._values["format"] = format
        if hierarchy is not None:
            self._values["hierarchy"] = hierarchy
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def format(self) -> typing.Optional["S3OutputFilePrefixFormat"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional["S3OutputFilePrefixFormat"], result)

    @builtins.property
    def hierarchy(self) -> typing.Optional[typing.List["S3OutputFilePrefixHierarchy"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("hierarchy")
        return typing.cast(typing.Optional[typing.List["S3OutputFilePrefixHierarchy"]], result)

    @builtins.property
    def type(self) -> typing.Optional["S3OutputFilePrefixType"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional["S3OutputFilePrefixType"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3OutputFilePrefix(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.S3OutputFilePrefixFormat")
class S3OutputFilePrefixFormat(enum.Enum):
    '''
    :stability: experimental
    '''

    DAY = "DAY"
    '''
    :stability: experimental
    '''
    HOUR = "HOUR"
    '''
    :stability: experimental
    '''
    MINUTE = "MINUTE"
    '''
    :stability: experimental
    '''
    MONTH = "MONTH"
    '''
    :stability: experimental
    '''
    YEAR = "YEAR"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.S3OutputFilePrefixHierarchy")
class S3OutputFilePrefixHierarchy(enum.Enum):
    '''
    :stability: experimental
    '''

    EXECUTION_ID = "EXECUTION_ID"
    '''
    :stability: experimental
    '''
    SCHEMA_VERSION = "SCHEMA_VERSION"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.S3OutputFilePrefixType")
class S3OutputFilePrefixType(enum.Enum):
    '''
    :stability: experimental
    '''

    FILENAME = "FILENAME"
    '''
    :stability: experimental
    '''
    PATH = "PATH"
    '''
    :stability: experimental
    '''
    PATH_AND_FILE = "PATH_AND_FILE"
    '''
    :stability: experimental
    '''


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.S3OutputFileType")
class S3OutputFileType(enum.Enum):
    '''(experimental) Output file type supported by Amazon S3 Destination connector.

    :stability: experimental
    '''

    CSV = "CSV"
    '''(experimental) CSV file type.

    :stability: experimental
    '''
    JSON = "JSON"
    '''(experimental) JSON file type.

    :stability: experimental
    '''
    PARQUET = "PARQUET"
    '''(experimental) Parquet file type.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3OutputFormatting",
    jsii_struct_bases=[],
    name_mapping={
        "aggregation": "aggregation",
        "file_prefix": "filePrefix",
        "file_type": "fileType",
        "preserve_source_data_types": "preserveSourceDataTypes",
    },
)
class S3OutputFormatting:
    def __init__(
        self,
        *,
        aggregation: typing.Optional[typing.Union[S3FileAggregation, typing.Dict[builtins.str, typing.Any]]] = None,
        file_prefix: typing.Optional[typing.Union[S3OutputFilePrefix, typing.Dict[builtins.str, typing.Any]]] = None,
        file_type: typing.Optional[S3OutputFileType] = None,
        preserve_source_data_types: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param aggregation: (experimental) Sets an aggregation approach per flow run.
        :param file_prefix: (experimental) Sets a prefix approach for files generated during a flow execution.
        :param file_type: (experimental) Sets the file type for the output files. Default: - JSON file type
        :param preserve_source_data_types: (experimental) Specifies whether AppFlow should attempt data type mapping from source when the destination output file type is Parquet. Default: - do not preserve source data files

        :stability: experimental
        '''
        if isinstance(aggregation, dict):
            aggregation = S3FileAggregation(**aggregation)
        if isinstance(file_prefix, dict):
            file_prefix = S3OutputFilePrefix(**file_prefix)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__647c5a42bd0a3abbe0881bec37a2f5f356717ea5a7051431c18f534fd0fafa8c)
            check_type(argname="argument aggregation", value=aggregation, expected_type=type_hints["aggregation"])
            check_type(argname="argument file_prefix", value=file_prefix, expected_type=type_hints["file_prefix"])
            check_type(argname="argument file_type", value=file_type, expected_type=type_hints["file_type"])
            check_type(argname="argument preserve_source_data_types", value=preserve_source_data_types, expected_type=type_hints["preserve_source_data_types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aggregation is not None:
            self._values["aggregation"] = aggregation
        if file_prefix is not None:
            self._values["file_prefix"] = file_prefix
        if file_type is not None:
            self._values["file_type"] = file_type
        if preserve_source_data_types is not None:
            self._values["preserve_source_data_types"] = preserve_source_data_types

    @builtins.property
    def aggregation(self) -> typing.Optional[S3FileAggregation]:
        '''(experimental) Sets an aggregation approach per flow run.

        :stability: experimental
        '''
        result = self._values.get("aggregation")
        return typing.cast(typing.Optional[S3FileAggregation], result)

    @builtins.property
    def file_prefix(self) -> typing.Optional[S3OutputFilePrefix]:
        '''(experimental) Sets a prefix approach for files generated during a flow execution.

        :stability: experimental
        '''
        result = self._values.get("file_prefix")
        return typing.cast(typing.Optional[S3OutputFilePrefix], result)

    @builtins.property
    def file_type(self) -> typing.Optional[S3OutputFileType]:
        '''(experimental) Sets the file type for the output files.

        :default: - JSON file type

        :stability: experimental
        '''
        result = self._values.get("file_type")
        return typing.cast(typing.Optional[S3OutputFileType], result)

    @builtins.property
    def preserve_source_data_types(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Specifies whether AppFlow should attempt data type mapping from source when the destination output file type is Parquet.

        :default: - do not preserve source data files

        :stability: experimental
        '''
        result = self._values.get("preserve_source_data_types")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3OutputFormatting(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.S3SourceProps",
    jsii_struct_bases=[],
    name_mapping={"bucket": "bucket", "prefix": "prefix", "format": "format"},
)
class S3SourceProps:
    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        prefix: builtins.str,
        format: typing.Optional[typing.Union[S3InputFormat, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bucket: 
        :param prefix: 
        :param format: 

        :stability: experimental
        '''
        if isinstance(format, dict):
            format = S3InputFormat(**format)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11add0251725b085f566155764021eaac6c26a1c71db654617abc2f9d41fc41d)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bucket": bucket,
            "prefix": prefix,
        }
        if format is not None:
            self._values["format"] = format

    @builtins.property
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''
        :stability: experimental
        '''
        result = self._values.get("bucket")
        assert result is not None, "Required property 'bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def prefix(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("prefix")
        assert result is not None, "Required property 'prefix' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def format(self) -> typing.Optional[S3InputFormat]:
        '''
        :stability: experimental
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[S3InputFormat], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "S3SourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataBasicAuthSettings",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class SAPOdataBasicAuthSettings:
    def __init__(
        self,
        *,
        password: _aws_cdk_ceddda9d.SecretValue,
        username: builtins.str,
    ) -> None:
        '''
        :param password: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce4c0b0b2383996eec6cecc0c36fb286975bc25afe5c2b0daf63e6f4df264179)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataBasicAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "application_host_url": "applicationHostUrl",
        "application_service_path": "applicationServicePath",
        "client_number": "clientNumber",
        "logon_language": "logonLanguage",
        "basic_auth": "basicAuth",
        "o_auth": "oAuth",
        "port_number": "portNumber",
    },
)
class SAPOdataConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        application_host_url: builtins.str,
        application_service_path: builtins.str,
        client_number: builtins.str,
        logon_language: builtins.str,
        basic_auth: typing.Optional[typing.Union[SAPOdataBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        o_auth: typing.Optional[typing.Union["SAPOdataOAuthSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        port_number: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param application_host_url: 
        :param application_service_path: 
        :param client_number: 
        :param logon_language: 
        :param basic_auth: 
        :param o_auth: 
        :param port_number: 

        :stability: experimental
        '''
        if isinstance(basic_auth, dict):
            basic_auth = SAPOdataBasicAuthSettings(**basic_auth)
        if isinstance(o_auth, dict):
            o_auth = SAPOdataOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c30df13ceca2f1ff215e11a4e86a5f6bd8a1245b181c59827c0daa29e8f90072)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument application_host_url", value=application_host_url, expected_type=type_hints["application_host_url"])
            check_type(argname="argument application_service_path", value=application_service_path, expected_type=type_hints["application_service_path"])
            check_type(argname="argument client_number", value=client_number, expected_type=type_hints["client_number"])
            check_type(argname="argument logon_language", value=logon_language, expected_type=type_hints["logon_language"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
            check_type(argname="argument port_number", value=port_number, expected_type=type_hints["port_number"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "application_host_url": application_host_url,
            "application_service_path": application_service_path,
            "client_number": client_number,
            "logon_language": logon_language,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if basic_auth is not None:
            self._values["basic_auth"] = basic_auth
        if o_auth is not None:
            self._values["o_auth"] = o_auth
        if port_number is not None:
            self._values["port_number"] = port_number

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def application_host_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("application_host_url")
        assert result is not None, "Required property 'application_host_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_service_path(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("application_service_path")
        assert result is not None, "Required property 'application_service_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def client_number(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_number")
        assert result is not None, "Required property 'client_number' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def logon_language(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("logon_language")
        assert result is not None, "Required property 'logon_language' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def basic_auth(self) -> typing.Optional[SAPOdataBasicAuthSettings]:
        '''
        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        return typing.cast(typing.Optional[SAPOdataBasicAuthSettings], result)

    @builtins.property
    def o_auth(self) -> typing.Optional["SAPOdataOAuthSettings"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        return typing.cast(typing.Optional["SAPOdataOAuthSettings"], result)

    @builtins.property
    def port_number(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("port_number")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "operation": "operation",
        "profile": "profile",
        "error_handling": "errorHandling",
        "success_response_handling": "successResponseHandling",
    },
)
class SAPOdataDestinationProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        operation: "WriteOperation",
        profile: "SAPOdataConnectorProfile",
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        success_response_handling: typing.Optional[typing.Union["SAPOdataSuccessResponseHandlingConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param object: (experimental) The SAPOdata object for which the operation is to be set.
        :param operation: 
        :param profile: 
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the SAPOdata destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.
        :param success_response_handling: 

        :stability: experimental
        '''
        if isinstance(error_handling, dict):
            error_handling = ErrorHandlingConfiguration(**error_handling)
        if isinstance(success_response_handling, dict):
            success_response_handling = SAPOdataSuccessResponseHandlingConfiguration(**success_response_handling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d90d6697fd4914c63c12e96e1fa677de8b617deda9d68e06597a1162de72ff46)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument error_handling", value=error_handling, expected_type=type_hints["error_handling"])
            check_type(argname="argument success_response_handling", value=success_response_handling, expected_type=type_hints["success_response_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "operation": operation,
            "profile": profile,
        }
        if error_handling is not None:
            self._values["error_handling"] = error_handling
        if success_response_handling is not None:
            self._values["success_response_handling"] = success_response_handling

    @builtins.property
    def object(self) -> builtins.str:
        '''(experimental) The SAPOdata object for which the operation is to be set.

        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operation(self) -> "WriteOperation":
        '''
        :stability: experimental
        '''
        result = self._values.get("operation")
        assert result is not None, "Required property 'operation' is missing"
        return typing.cast("WriteOperation", result)

    @builtins.property
    def profile(self) -> "SAPOdataConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("SAPOdataConnectorProfile", result)

    @builtins.property
    def error_handling(self) -> typing.Optional[ErrorHandlingConfiguration]:
        '''(experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the SAPOdata destination.

        For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        result = self._values.get("error_handling")
        return typing.cast(typing.Optional[ErrorHandlingConfiguration], result)

    @builtins.property
    def success_response_handling(
        self,
    ) -> typing.Optional["SAPOdataSuccessResponseHandlingConfiguration"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("success_response_handling")
        return typing.cast(typing.Optional["SAPOdataSuccessResponseHandlingConfiguration"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataOAuthEndpoints",
    jsii_struct_bases=[],
    name_mapping={"token": "token"},
)
class SAPOdataOAuthEndpoints:
    def __init__(self, *, token: builtins.str) -> None:
        '''
        :param token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da515d0d4648ceb542f575c8c56866e2466cb923c70d677cbc3a707ef221ccf4)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token": token,
        }

    @builtins.property
    def token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataOAuthEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataOAuthFlows",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class SAPOdataOAuthFlows:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Union["SAPOdataOAuthRefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param refresh_token_grant: 

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = SAPOdataOAuthRefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cefed30b945239087f3dbb8a1ddb5dabb6307d3d35e04ede5e4a6887f6d0d581)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "refresh_token_grant": refresh_token_grant,
        }

    @builtins.property
    def refresh_token_grant(self) -> "SAPOdataOAuthRefreshTokenGrantFlow":
        '''
        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        assert result is not None, "Required property 'refresh_token_grant' is missing"
        return typing.cast("SAPOdataOAuthRefreshTokenGrantFlow", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataOAuthFlows(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataOAuthRefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "refresh_token": "refreshToken",
    },
)
class SAPOdataOAuthRefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client_id: _aws_cdk_ceddda9d.SecretValue,
        client_secret: _aws_cdk_ceddda9d.SecretValue,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param client_id: 
        :param client_secret: 
        :param refresh_token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fff92b1fecd8fb687b0fb4bdc1411cb80fac93d1dfb20791ff4b5c327fd3b240)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client_id(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def client_secret(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataOAuthRefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "endpoints": "endpoints",
        "flow": "flow",
    },
)
class SAPOdataOAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        endpoints: typing.Optional[typing.Union[SAPOdataOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
        flow: typing.Optional[typing.Union[SAPOdataOAuthFlows, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: 
        :param endpoints: 
        :param flow: 

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = SAPOdataOAuthEndpoints(**endpoints)
        if isinstance(flow, dict):
            flow = SAPOdataOAuthFlows(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6c602c5338ef47ca8f8b846c7354c60a34e2b2a3c774b4e8c0581d482e6294f)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if endpoints is not None:
            self._values["endpoints"] = endpoints
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def endpoints(self) -> typing.Optional[SAPOdataOAuthEndpoints]:
        '''
        :stability: experimental
        '''
        result = self._values.get("endpoints")
        return typing.cast(typing.Optional[SAPOdataOAuthEndpoints], result)

    @builtins.property
    def flow(self) -> typing.Optional[SAPOdataOAuthFlows]:
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[SAPOdataOAuthFlows], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataSourceProps",
    jsii_struct_bases=[],
    name_mapping={"object": "object", "profile": "profile"},
)
class SAPOdataSourceProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        profile: "SAPOdataConnectorProfile",
    ) -> None:
        '''
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46c8000b7de41ff27d29d18565fcd6f07d4e7be2d898c826689b0a5ee0cc9835)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "SAPOdataConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("SAPOdataConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SAPOdataSuccessResponseHandlingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"location": "location"},
)
class SAPOdataSuccessResponseHandlingConfiguration:
    def __init__(
        self,
        *,
        location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param location: 

        :stability: experimental
        '''
        if isinstance(location, dict):
            location = S3Location(**location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ed6c082cacef689ea56d955987bb16bb38ebfbc22ac5a9953c1609643d6ef5)
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "location": location,
        }

    @builtins.property
    def location(self) -> S3Location:
        '''
        :stability: experimental
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(S3Location, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SAPOdataSuccessResponseHandlingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "instance_url": "instanceUrl",
        "o_auth": "oAuth",
        "is_sandbox": "isSandbox",
    },
)
class SalesforceConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        instance_url: builtins.str,
        o_auth: typing.Union["SalesforceOAuthSettings", typing.Dict[builtins.str, typing.Any]],
        is_sandbox: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param instance_url: 
        :param o_auth: 
        :param is_sandbox: Default: false

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = SalesforceOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb386fe4c6e6ec8ddee55dea0effc0a7bd692124b527bb2ffbb3554ffd2a04ee)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
            check_type(argname="argument is_sandbox", value=is_sandbox, expected_type=type_hints["is_sandbox"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_url": instance_url,
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if is_sandbox is not None:
            self._values["is_sandbox"] = is_sandbox

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def o_auth(self) -> "SalesforceOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("SalesforceOAuthSettings", result)

    @builtins.property
    def is_sandbox(self) -> typing.Optional[builtins.bool]:
        '''
        :default: false

        :stability: experimental
        '''
        result = self._values.get("is_sandbox")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.SalesforceDataTransferApi")
class SalesforceDataTransferApi(enum.Enum):
    '''(experimental) The default.

    Amazon AppFlow selects which API to use based on the number of records that your flow transfers to Salesforce. If your flow transfers fewer than 1,000 records, Amazon AppFlow uses Salesforce REST API. If your flow transfers 1,000 records or more, Amazon AppFlow uses Salesforce Bulk API 2.0.

    Each of these Salesforce APIs structures data differently. If Amazon AppFlow selects the API automatically, be aware that, for recurring flows, the data output might vary from one flow run to the next. For example, if a flow runs daily, it might use REST API on one day to transfer 900 records, and it might use Bulk API 2.0 on the next day to transfer 1,100 records. For each of these flow runs, the respective Salesforce API formats the data differently. Some of the differences include how dates are formatted and null values are represented. Also, Bulk API 2.0 doesn't transfer Salesforce compound fields.

    By choosing this option, you optimize flow performance for both small and large data transfers, but the tradeoff is inconsistent formatting in the output.

    :stability: experimental
    '''

    AUTOMATIC = "AUTOMATIC"
    '''
    :stability: experimental
    '''
    BULKV2 = "BULKV2"
    '''
    :stability: experimental
    '''
    REST_SYNC = "REST_SYNC"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "operation": "operation",
        "profile": "profile",
        "data_transfer_api": "dataTransferApi",
        "error_handling": "errorHandling",
    },
)
class SalesforceDestinationProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        operation: "WriteOperation",
        profile: "SalesforceConnectorProfile",
        data_transfer_api: typing.Optional[SalesforceDataTransferApi] = None,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param object: (experimental) The Salesforce object for which the operation is to be set.
        :param operation: 
        :param profile: 
        :param data_transfer_api: (experimental) Specifies which Salesforce API is used by Amazon AppFlow when your flow transfers data to Salesforce.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        if isinstance(error_handling, dict):
            error_handling = ErrorHandlingConfiguration(**error_handling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26af46d5b920211884966f102c2c1f731758b3a81197ca9ea732b4a377afecd4)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument data_transfer_api", value=data_transfer_api, expected_type=type_hints["data_transfer_api"])
            check_type(argname="argument error_handling", value=error_handling, expected_type=type_hints["error_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "operation": operation,
            "profile": profile,
        }
        if data_transfer_api is not None:
            self._values["data_transfer_api"] = data_transfer_api
        if error_handling is not None:
            self._values["error_handling"] = error_handling

    @builtins.property
    def object(self) -> builtins.str:
        '''(experimental) The Salesforce object for which the operation is to be set.

        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operation(self) -> "WriteOperation":
        '''
        :stability: experimental
        '''
        result = self._values.get("operation")
        assert result is not None, "Required property 'operation' is missing"
        return typing.cast("WriteOperation", result)

    @builtins.property
    def profile(self) -> "SalesforceConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("SalesforceConnectorProfile", result)

    @builtins.property
    def data_transfer_api(self) -> typing.Optional[SalesforceDataTransferApi]:
        '''(experimental) Specifies which Salesforce API is used by Amazon AppFlow when your flow transfers data to Salesforce.

        :stability: experimental
        '''
        result = self._values.get("data_transfer_api")
        return typing.cast(typing.Optional[SalesforceDataTransferApi], result)

    @builtins.property
    def error_handling(self) -> typing.Optional[ErrorHandlingConfiguration]:
        '''(experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination.

        For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        result = self._values.get("error_handling")
        return typing.cast(typing.Optional[ErrorHandlingConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudApiVersions")
class SalesforceMarketingCloudApiVersions(enum.Enum):
    '''(experimental) A helper enum for SFMC api version.

    :stability: experimental
    '''

    V1 = "V1"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "instance_url": "instanceUrl",
        "o_auth": "oAuth",
    },
)
class SalesforceMarketingCloudConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        instance_url: builtins.str,
        o_auth: typing.Union["SalesforceMarketingCloudOAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param instance_url: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = SalesforceMarketingCloudOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f99b5a5bb33f8ce8861da82005fc5c2a43bf5508c1b5c06cc8ca4e4a6d4105f8)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_url": instance_url,
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def o_auth(self) -> "SalesforceMarketingCloudOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("SalesforceMarketingCloudOAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceMarketingCloudConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudFlowSettings",
    jsii_struct_bases=[],
    name_mapping={"client_credentials": "clientCredentials"},
)
class SalesforceMarketingCloudFlowSettings:
    def __init__(
        self,
        *,
        client_credentials: typing.Union["SalesforceMarketingCloudOAuthClientSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param client_credentials: 

        :stability: experimental
        '''
        if isinstance(client_credentials, dict):
            client_credentials = SalesforceMarketingCloudOAuthClientSettings(**client_credentials)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c57117565965b356b2a164ff026a738bf39d9737f2ca6fa64ed370537b81894a)
            check_type(argname="argument client_credentials", value=client_credentials, expected_type=type_hints["client_credentials"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_credentials": client_credentials,
        }

    @builtins.property
    def client_credentials(self) -> "SalesforceMarketingCloudOAuthClientSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("client_credentials")
        assert result is not None, "Required property 'client_credentials' is missing"
        return typing.cast("SalesforceMarketingCloudOAuthClientSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceMarketingCloudFlowSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudOAuthClientSettings",
    jsii_struct_bases=[],
    name_mapping={"client_id": "clientId", "client_secret": "clientSecret"},
)
class SalesforceMarketingCloudOAuthClientSettings:
    def __init__(
        self,
        *,
        client_id: _aws_cdk_ceddda9d.SecretValue,
        client_secret: _aws_cdk_ceddda9d.SecretValue,
    ) -> None:
        '''
        :param client_id: 
        :param client_secret: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96bd44a4c49d944fa430925f47eb270e0c8112c56b8100f96cefcfb18b121a1b)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_id": client_id,
            "client_secret": client_secret,
        }

    @builtins.property
    def client_id(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def client_secret(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceMarketingCloudOAuthClientSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudOAuthEndpoints",
    jsii_struct_bases=[],
    name_mapping={"token": "token"},
)
class SalesforceMarketingCloudOAuthEndpoints:
    def __init__(self, *, token: builtins.str) -> None:
        '''
        :param token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcff86daa0f6250709c4f5188043150713c1b07212980cb196f7953d27bbca74)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token": token,
        }

    @builtins.property
    def token(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceMarketingCloudOAuthEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "endpoints": "endpoints",
        "access_token": "accessToken",
        "flow": "flow",
    },
)
class SalesforceMarketingCloudOAuthSettings:
    def __init__(
        self,
        *,
        endpoints: typing.Union[SalesforceMarketingCloudOAuthEndpoints, typing.Dict[builtins.str, typing.Any]],
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        flow: typing.Optional[typing.Union[SalesforceMarketingCloudFlowSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param endpoints: 
        :param access_token: 
        :param flow: 

        :stability: experimental
        '''
        if isinstance(endpoints, dict):
            endpoints = SalesforceMarketingCloudOAuthEndpoints(**endpoints)
        if isinstance(flow, dict):
            flow = SalesforceMarketingCloudFlowSettings(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2121dcb2c9866dc66748863d722c2e24692a091e9e083497b7e972827e5ec10f)
            check_type(argname="argument endpoints", value=endpoints, expected_type=type_hints["endpoints"])
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "endpoints": endpoints,
        }
        if access_token is not None:
            self._values["access_token"] = access_token
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def endpoints(self) -> SalesforceMarketingCloudOAuthEndpoints:
        '''
        :stability: experimental
        '''
        result = self._values.get("endpoints")
        assert result is not None, "Required property 'endpoints' is missing"
        return typing.cast(SalesforceMarketingCloudOAuthEndpoints, result)

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def flow(self) -> typing.Optional[SalesforceMarketingCloudFlowSettings]:
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[SalesforceMarketingCloudFlowSettings], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceMarketingCloudOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "api_version": "apiVersion",
        "object": "object",
        "profile": "profile",
    },
)
class SalesforceMarketingCloudSourceProps:
    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: "SalesforceMarketingCloudConnectorProfile",
    ) -> None:
        '''(experimental) Properties of a Salesforce Marketing Cloud Source.

        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fffd1efba2dc38fee00bedf5fe2bb6dd15b6a55e87350eafa49ced8cfdaa5d1b)
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "api_version": api_version,
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def api_version(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        assert result is not None, "Required property 'api_version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "SalesforceMarketingCloudConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("SalesforceMarketingCloudConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceMarketingCloudSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceOAuthFlow",
    jsii_struct_bases=[],
    name_mapping={"refresh_token_grant": "refreshTokenGrant"},
)
class SalesforceOAuthFlow:
    def __init__(
        self,
        *,
        refresh_token_grant: typing.Optional[typing.Union["SalesforceOAuthRefreshTokenGrantFlow", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param refresh_token_grant: (experimental) The parameters required for the refresh token grant OAuth flow.

        :stability: experimental
        '''
        if isinstance(refresh_token_grant, dict):
            refresh_token_grant = SalesforceOAuthRefreshTokenGrantFlow(**refresh_token_grant)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bb20287992df1bb2824bccc50aa824c16613f769993cb06ee2d3bd7bd25daee)
            check_type(argname="argument refresh_token_grant", value=refresh_token_grant, expected_type=type_hints["refresh_token_grant"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if refresh_token_grant is not None:
            self._values["refresh_token_grant"] = refresh_token_grant

    @builtins.property
    def refresh_token_grant(
        self,
    ) -> typing.Optional["SalesforceOAuthRefreshTokenGrantFlow"]:
        '''(experimental) The parameters required for the refresh token grant OAuth flow.

        :stability: experimental
        '''
        result = self._values.get("refresh_token_grant")
        return typing.cast(typing.Optional["SalesforceOAuthRefreshTokenGrantFlow"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceOAuthFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceOAuthRefreshTokenGrantFlow",
    jsii_struct_bases=[],
    name_mapping={"client": "client", "refresh_token": "refreshToken"},
)
class SalesforceOAuthRefreshTokenGrantFlow:
    def __init__(
        self,
        *,
        client: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
        refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param client: 
        :param refresh_token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e4b4bc6fd4f76d44c56b32d530c5958a5d59603bbdcba534918f88312b2213)
            check_type(argname="argument client", value=client, expected_type=type_hints["client"])
            check_type(argname="argument refresh_token", value=refresh_token, expected_type=type_hints["refresh_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if client is not None:
            self._values["client"] = client
        if refresh_token is not None:
            self._values["refresh_token"] = refresh_token

    @builtins.property
    def client(self) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    @builtins.property
    def refresh_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("refresh_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceOAuthRefreshTokenGrantFlow(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={"access_token": "accessToken", "flow": "flow"},
)
class SalesforceOAuthSettings:
    def __init__(
        self,
        *,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        flow: typing.Optional[typing.Union[SalesforceOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param access_token: 
        :param flow: 

        :stability: experimental
        '''
        if isinstance(flow, dict):
            flow = SalesforceOAuthFlow(**flow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b3d2312e8e6dbe607505cbf86b95e10be30b1477e042903f79af94a19fb24a6)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_token is not None:
            self._values["access_token"] = access_token
        if flow is not None:
            self._values["flow"] = flow

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def flow(self) -> typing.Optional[SalesforceOAuthFlow]:
        '''
        :stability: experimental
        '''
        result = self._values.get("flow")
        return typing.cast(typing.Optional[SalesforceOAuthFlow], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SalesforceSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "api_version": "apiVersion",
        "data_transfer_api": "dataTransferApi",
        "enable_dynamic_field_update": "enableDynamicFieldUpdate",
        "include_deleted_records": "includeDeletedRecords",
    },
)
class SalesforceSourceProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        profile: "SalesforceConnectorProfile",
        api_version: typing.Optional[builtins.str] = None,
        data_transfer_api: typing.Optional[SalesforceDataTransferApi] = None,
        enable_dynamic_field_update: typing.Optional[builtins.bool] = None,
        include_deleted_records: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 
        :param data_transfer_api: (experimental) Specifies which Salesforce API is used by Amazon AppFlow when your flow transfers data from Salesforce.
        :param enable_dynamic_field_update: 
        :param include_deleted_records: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30d372f25a17b9521a450436c8487a90f4bb05f9b654a2ae6047526cb28bc529)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
            check_type(argname="argument data_transfer_api", value=data_transfer_api, expected_type=type_hints["data_transfer_api"])
            check_type(argname="argument enable_dynamic_field_update", value=enable_dynamic_field_update, expected_type=type_hints["enable_dynamic_field_update"])
            check_type(argname="argument include_deleted_records", value=include_deleted_records, expected_type=type_hints["include_deleted_records"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if api_version is not None:
            self._values["api_version"] = api_version
        if data_transfer_api is not None:
            self._values["data_transfer_api"] = data_transfer_api
        if enable_dynamic_field_update is not None:
            self._values["enable_dynamic_field_update"] = enable_dynamic_field_update
        if include_deleted_records is not None:
            self._values["include_deleted_records"] = include_deleted_records

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "SalesforceConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("SalesforceConnectorProfile", result)

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_transfer_api(self) -> typing.Optional[SalesforceDataTransferApi]:
        '''(experimental) Specifies which Salesforce API is used by Amazon AppFlow when your flow transfers data from Salesforce.

        :stability: experimental
        '''
        result = self._values.get("data_transfer_api")
        return typing.cast(typing.Optional[SalesforceDataTransferApi], result)

    @builtins.property
    def enable_dynamic_field_update(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("enable_dynamic_field_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def include_deleted_records(self) -> typing.Optional[builtins.bool]:
        '''
        :stability: experimental
        '''
        result = self._values.get("include_deleted_records")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SalesforceSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ScheduleProperties",
    jsii_struct_bases=[],
    name_mapping={
        "end_time": "endTime",
        "first_execution_from": "firstExecutionFrom",
        "offset": "offset",
        "start_time": "startTime",
    },
)
class ScheduleProperties:
    def __init__(
        self,
        *,
        end_time: typing.Optional[datetime.datetime] = None,
        first_execution_from: typing.Optional[datetime.datetime] = None,
        offset: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        start_time: typing.Optional[datetime.datetime] = None,
    ) -> None:
        '''
        :param end_time: 
        :param first_execution_from: (experimental) Timestamp for the records to import from the connector in the first flow run. Default: 30 days back from the initial frow run
        :param offset: 
        :param start_time: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0a2f97eb1106a2fa425f6885698e656218767d3d41fc35a8560b8aeec3a8720)
            check_type(argname="argument end_time", value=end_time, expected_type=type_hints["end_time"])
            check_type(argname="argument first_execution_from", value=first_execution_from, expected_type=type_hints["first_execution_from"])
            check_type(argname="argument offset", value=offset, expected_type=type_hints["offset"])
            check_type(argname="argument start_time", value=start_time, expected_type=type_hints["start_time"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if end_time is not None:
            self._values["end_time"] = end_time
        if first_execution_from is not None:
            self._values["first_execution_from"] = first_execution_from
        if offset is not None:
            self._values["offset"] = offset
        if start_time is not None:
            self._values["start_time"] = start_time

    @builtins.property
    def end_time(self) -> typing.Optional[datetime.datetime]:
        '''
        :stability: experimental
        '''
        result = self._values.get("end_time")
        return typing.cast(typing.Optional[datetime.datetime], result)

    @builtins.property
    def first_execution_from(self) -> typing.Optional[datetime.datetime]:
        '''(experimental) Timestamp for the records to import from the connector in the first flow run.

        :default: 30 days back from the initial frow run

        :stability: experimental
        '''
        result = self._values.get("first_execution_from")
        return typing.cast(typing.Optional[datetime.datetime], result)

    @builtins.property
    def offset(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''
        :stability: experimental
        '''
        result = self._values.get("offset")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def start_time(self) -> typing.Optional[datetime.datetime]:
        '''
        :stability: experimental
        '''
        result = self._values.get("start_time")
        return typing.cast(typing.Optional[datetime.datetime], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ScheduleProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ServiceNowBasicSettings",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class ServiceNowBasicSettings:
    def __init__(
        self,
        *,
        password: _aws_cdk_ceddda9d.SecretValue,
        username: builtins.str,
    ) -> None:
        '''
        :param password: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35c555741db534372681a356953cf08bac7dc48ca53b011426d5a7eabe6b2255)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceNowBasicSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ServiceNowConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "basic_auth": "basicAuth",
        "instance_url": "instanceUrl",
    },
)
class ServiceNowConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        basic_auth: typing.Union[ServiceNowBasicSettings, typing.Dict[builtins.str, typing.Any]],
        instance_url: builtins.str,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param basic_auth: 
        :param instance_url: 

        :stability: experimental
        '''
        if isinstance(basic_auth, dict):
            basic_auth = ServiceNowBasicSettings(**basic_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63673f65488910421fc09fc00bac26db0a7f26ac179c42060b98bec55fec912e)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "basic_auth": basic_auth,
            "instance_url": instance_url,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def basic_auth(self) -> ServiceNowBasicSettings:
        '''
        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        assert result is not None, "Required property 'basic_auth' is missing"
        return typing.cast(ServiceNowBasicSettings, result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceNowConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ServiceNowInstanceUrlBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ServiceNowInstanceUrlBuilder",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildFromDomain")
    @builtins.classmethod
    def build_from_domain(cls, domain: builtins.str) -> builtins.str:
        '''
        :param domain: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad25ad6831ab64e0fadd9ceeda1adc39130b601638da4a9cdd3e82d64afbb722)
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "buildFromDomain", [domain]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ServiceNowSourceProps",
    jsii_struct_bases=[],
    name_mapping={"object": "object", "profile": "profile"},
)
class ServiceNowSourceProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        profile: "ServiceNowConnectorProfile",
    ) -> None:
        '''
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed901b4674fdd5b5d8aca2d28fbdf744d228510b752e4514767f32208c2ffc3)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "ServiceNowConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("ServiceNowConnectorProfile", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceNowSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SlackConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "instance_url": "instanceUrl",
        "o_auth": "oAuth",
    },
)
class SlackConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        instance_url: builtins.str,
        o_auth: typing.Union["SlackOAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param instance_url: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = SlackOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3366bcfa4a8faf3ddcc2d8352e6dcdb18f40aaa06c7029081e80039b2777ad0)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_url": instance_url,
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def o_auth(self) -> "SlackOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("SlackOAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackInstanceUrlBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SlackInstanceUrlBuilder",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildFromWorkspace")
    @builtins.classmethod
    def build_from_workspace(cls, workspace: builtins.str) -> builtins.str:
        '''
        :param workspace: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb08209450125f2e8479d608154ce728f1d90ffdbfc2b59d68cbe461fc268983)
            check_type(argname="argument workspace", value=workspace, expected_type=type_hints["workspace"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "buildFromWorkspace", [workspace]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SlackOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "access_token": "accessToken",
        "client_id": "clientId",
        "client_secret": "clientSecret",
    },
)
class SlackOAuthSettings:
    def __init__(
        self,
        *,
        access_token: _aws_cdk_ceddda9d.SecretValue,
        client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param access_token: 
        :param client_id: 
        :param client_secret: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c85d508ca7011bdf2ded0cf3b5e9fdc6fcc5539051311b7c2170f93564ea838)
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_token": access_token,
        }
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret

    @builtins.property
    def access_token(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("access_token")
        assert result is not None, "Required property 'access_token' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def client_id(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SlackSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "api_version": "apiVersion",
    },
)
class SlackSourceProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        profile: "SlackConnectorProfile",
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0e4d776743bda8a375dea1e95823dd583e550a30280bd3b02143312f8d17cec)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if api_version is not None:
            self._values["api_version"] = api_version

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "SlackConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("SlackConnectorProfile", result)

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SnowflakeBasicAuthSettings",
    jsii_struct_bases=[],
    name_mapping={"password": "password", "username": "username"},
)
class SnowflakeBasicAuthSettings:
    def __init__(
        self,
        *,
        password: _aws_cdk_ceddda9d.SecretValue,
        username: builtins.str,
    ) -> None:
        '''(experimental) Snowflake authorization settings required for the profile.

        :param password: 
        :param username: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d7db9d78ada1829fc032eed083a5d0fe61002cd2949f410b164b6a2aa8d19a7)
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password": password,
            "username": username,
        }

    @builtins.property
    def password(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("password")
        assert result is not None, "Required property 'password' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def username(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnowflakeBasicAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SnowflakeConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "account": "account",
        "basic_auth": "basicAuth",
        "database": "database",
        "location": "location",
        "stage": "stage",
        "warehouse": "warehouse",
        "integration": "integration",
        "region": "region",
        "schema": "schema",
    },
)
class SnowflakeConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        account: builtins.str,
        basic_auth: typing.Union[SnowflakeBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
        database: builtins.str,
        location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
        stage: builtins.str,
        warehouse: builtins.str,
        integration: typing.Optional[typing.Union["SnowflakeStorageIntegration", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for a Snowflake connectorprofile.

        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param account: 
        :param basic_auth: 
        :param database: (experimental) The name of the Snowflake database.
        :param location: 
        :param stage: (experimental) The name of the Snowflake stage.
        :param warehouse: (experimental) The name of the Snowflake warehouse.
        :param integration: (experimental) Details of the Snowflake Storage Integration. When provided, this construct will automatically create an IAM Role allowing access to the S3 Bucket which will be available as a [integrationROle property]{@link SnowflakeConnectorProfile#integrationRole } For details of the integration see {@link https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration}
        :param region: 
        :param schema: (experimental) The name of the Snowflake schema. Default: PUBLIC

        :stability: experimental
        '''
        if isinstance(basic_auth, dict):
            basic_auth = SnowflakeBasicAuthSettings(**basic_auth)
        if isinstance(location, dict):
            location = S3Location(**location)
        if isinstance(integration, dict):
            integration = SnowflakeStorageIntegration(**integration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__741297c13658831cfda5a41ceb6e41a3d0a3f3ab7415a9950c3d342ae37f2ab7)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
            check_type(argname="argument warehouse", value=warehouse, expected_type=type_hints["warehouse"])
            check_type(argname="argument integration", value=integration, expected_type=type_hints["integration"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument schema", value=schema, expected_type=type_hints["schema"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account": account,
            "basic_auth": basic_auth,
            "database": database,
            "location": location,
            "stage": stage,
            "warehouse": warehouse,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if integration is not None:
            self._values["integration"] = integration
        if region is not None:
            self._values["region"] = region
        if schema is not None:
            self._values["schema"] = schema

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def account(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("account")
        assert result is not None, "Required property 'account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def basic_auth(self) -> SnowflakeBasicAuthSettings:
        '''
        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        assert result is not None, "Required property 'basic_auth' is missing"
        return typing.cast(SnowflakeBasicAuthSettings, result)

    @builtins.property
    def database(self) -> builtins.str:
        '''(experimental) The name of the Snowflake database.

        :stability: experimental
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> S3Location:
        '''
        :stability: experimental
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(S3Location, result)

    @builtins.property
    def stage(self) -> builtins.str:
        '''(experimental) The name of the Snowflake stage.

        :stability: experimental
        '''
        result = self._values.get("stage")
        assert result is not None, "Required property 'stage' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def warehouse(self) -> builtins.str:
        '''(experimental) The name of the Snowflake warehouse.

        :stability: experimental
        '''
        result = self._values.get("warehouse")
        assert result is not None, "Required property 'warehouse' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def integration(self) -> typing.Optional["SnowflakeStorageIntegration"]:
        '''(experimental) Details of the Snowflake Storage Integration.

        When provided, this construct will automatically create an IAM Role allowing access to the S3 Bucket which will be available as a [integrationROle property]{@link SnowflakeConnectorProfile#integrationRole }

        For details of the integration see {@link https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration}

        :stability: experimental
        '''
        result = self._values.get("integration")
        return typing.cast(typing.Optional["SnowflakeStorageIntegration"], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def schema(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the Snowflake schema.

        :default: PUBLIC

        :stability: experimental
        '''
        result = self._values.get("schema")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnowflakeConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SnowflakeDestinationObject",
    jsii_struct_bases=[],
    name_mapping={"table": "table"},
)
class SnowflakeDestinationObject:
    def __init__(self, *, table: builtins.str) -> None:
        '''(experimental) The destination table in Snowflake.

        The table needs to reside in the databas and schema provided in the profile.

        :param table: (experimental) The name of the table object.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98eee9aad789e1c5f53d3d3a38169512e40be7865c4c7cce212218790009d32e)
            check_type(argname="argument table", value=table, expected_type=type_hints["table"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table": table,
        }

    @builtins.property
    def table(self) -> builtins.str:
        '''(experimental) The name of the table object.

        :stability: experimental
        '''
        result = self._values.get("table")
        assert result is not None, "Required property 'table' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnowflakeDestinationObject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SnowflakeDestinationProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "error_handling": "errorHandling",
    },
)
class SnowflakeDestinationProps:
    def __init__(
        self,
        *,
        object: typing.Union[SnowflakeDestinationObject, typing.Dict[builtins.str, typing.Any]],
        profile: "SnowflakeConnectorProfile",
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Properties that are required to create a Snowflake destination.

        :param object: (experimental) A Snowflake table object (optionally with the schema).
        :param profile: (experimental) A Snowflake connector profile instance.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        if isinstance(object, dict):
            object = SnowflakeDestinationObject(**object)
        if isinstance(error_handling, dict):
            error_handling = ErrorHandlingConfiguration(**error_handling)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f80b375007188911005c4fd1c96aa7c040f5466ec3e3d70f49b5dbf3e6462687)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument error_handling", value=error_handling, expected_type=type_hints["error_handling"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if error_handling is not None:
            self._values["error_handling"] = error_handling

    @builtins.property
    def object(self) -> SnowflakeDestinationObject:
        '''(experimental) A Snowflake table object (optionally with the schema).

        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(SnowflakeDestinationObject, result)

    @builtins.property
    def profile(self) -> "SnowflakeConnectorProfile":
        '''(experimental) A Snowflake connector profile instance.

        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("SnowflakeConnectorProfile", result)

    @builtins.property
    def error_handling(self) -> typing.Optional[ErrorHandlingConfiguration]:
        '''(experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination.

        For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        result = self._values.get("error_handling")
        return typing.cast(typing.Optional[ErrorHandlingConfiguration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnowflakeDestinationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.SnowflakeStorageIntegration",
    jsii_struct_bases=[],
    name_mapping={"external_id": "externalId", "storage_user_arn": "storageUserArn"},
)
class SnowflakeStorageIntegration:
    def __init__(
        self,
        *,
        external_id: builtins.str,
        storage_user_arn: builtins.str,
    ) -> None:
        '''
        :param external_id: 
        :param storage_user_arn: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8e0ca5f0d4687c015b4915a3dac207a7de1a514c0f968248ed4dec2a6c8d2ac)
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument storage_user_arn", value=storage_user_arn, expected_type=type_hints["storage_user_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "external_id": external_id,
            "storage_user_arn": storage_user_arn,
        }

    @builtins.property
    def external_id(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("external_id")
        assert result is not None, "Required property 'external_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def storage_user_arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("storage_user_arn")
        assert result is not None, "Required property 'storage_user_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SnowflakeStorageIntegration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ITask)
class Task(metaclass=jsii.JSIIMeta, jsii_type="@cdklabs/cdk-appflow.Task"):
    '''(experimental) A representation of a unitary action on the record fields.

    :stability: experimental
    '''

    def __init__(
        self,
        type: builtins.str,
        source_fields: typing.Sequence[builtins.str],
        connector_operator: typing.Union["TaskConnectorOperator", typing.Dict[builtins.str, typing.Any]],
        properties: typing.Sequence[typing.Union["TaskProperty", typing.Dict[builtins.str, typing.Any]]],
        destination_field: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: -
        :param source_fields: -
        :param connector_operator: -
        :param properties: -
        :param destination_field: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24692fc26478ce2d71b63bb5cb3aad2dce8ab876ef9bcb1fe29cc22712b96603)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument source_fields", value=source_fields, expected_type=type_hints["source_fields"])
            check_type(argname="argument connector_operator", value=connector_operator, expected_type=type_hints["connector_operator"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
            check_type(argname="argument destination_field", value=destination_field, expected_type=type_hints["destination_field"])
        jsii.create(self.__class__, self, [type, source_fields, connector_operator, properties, destination_field])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        _flow: IFlow,
        source: "ISource",
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty:
        '''
        :param _flow: -
        :param source: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6128ea3ff1cb4e2e28beece9552596b5334b2f91d87f23bc6895ad8e3da19705)
            check_type(argname="argument _flow", value=_flow, expected_type=type_hints["_flow"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.TaskProperty, jsii.invoke(self, "bind", [_flow, source]))

    @builtins.property
    @jsii.member(jsii_name="connectorOperator")
    def _connector_operator(self) -> "TaskConnectorOperator":
        '''
        :stability: experimental
        '''
        return typing.cast("TaskConnectorOperator", jsii.get(self, "connectorOperator"))

    @_connector_operator.setter
    def _connector_operator(self, value: "TaskConnectorOperator") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c287db748553ab89efc05e6ed00d913c713709726c7d10b4844f66cba313313d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectorOperator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="properties")
    def _properties(self) -> typing.List["TaskProperty"]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List["TaskProperty"], jsii.get(self, "properties"))

    @_properties.setter
    def _properties(self, value: typing.List["TaskProperty"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0eeab5d21f2d3f7741e64d02a9bdad89aeeaf57cd56a47a04c058b099d1e6649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "properties", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceFields")
    def _source_fields(self) -> typing.List[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sourceFields"))

    @_source_fields.setter
    def _source_fields(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f40185ac47e4693214d2d99ed5b935e3499b032a5920f9938a3c72fb8e6270de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceFields", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def _type(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @_type.setter
    def _type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e9446eb1c419044c87ad7f9339e6287c76df820ed89f50bab39f0059b3d6b50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="destinationField")
    def _destination_field(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationField"))

    @_destination_field.setter
    def _destination_field(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ba0519612063188a23f4ad3daf76a759533cfc1addfd48d040e60b2e3d6a1cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationField", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.TaskConnectorOperator",
    jsii_struct_bases=[],
    name_mapping={"operation": "operation", "type": "type"},
)
class TaskConnectorOperator:
    def __init__(
        self,
        *,
        operation: builtins.str,
        type: typing.Optional[ConnectorType] = None,
    ) -> None:
        '''(experimental) A pair that represents the (typically source) connector, and a task operation to be performed in the context of the connector.

        :param operation: 
        :param type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398aead5d0bd8510768d3927e715f426a75f799690a7ec9da8469770e0170e2b)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "operation": operation,
        }
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def operation(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("operation")
        assert result is not None, "Required property 'operation' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> typing.Optional[ConnectorType]:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[ConnectorType], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskConnectorOperator(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.TaskProperty",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class TaskProperty:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: 
        :param value: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1b051bd387400fdca98fdb91ffc4aaf76026ad8dbe494f487221d94253d9472)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(ITransform)
class Transform(
    OperationBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.Transform",
):
    '''(experimental) A representation of a transform operation, that is an operation modifying source fields.

    :stability: experimental
    '''

    def __init__(self, tasks: typing.Sequence[ITask]) -> None:
        '''
        :param tasks: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87a06aecfdef9894d45526cc1334c77d31cee6f12306317692baa83368d553f4)
            check_type(argname="argument tasks", value=tasks, expected_type=type_hints["tasks"])
        jsii.create(self.__class__, self, [tasks])

    @jsii.member(jsii_name="mask")
    @builtins.classmethod
    def mask(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
        mask: typing.Optional[builtins.str] = None,
    ) -> ITransform:
        '''(experimental) Masks the field with a specified mask.

        :param field: a source field to mask.
        :param mask: a mask character.

        :default: '*'

        :return: a

        :see: Transform instance
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c41a4351b279826717987e6ab9ce3182aa8f0612255630693a7292c8744f81ae)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument mask", value=mask, expected_type=type_hints["mask"])
        return typing.cast(ITransform, jsii.sinvoke(cls, "mask", [field, mask]))

    @jsii.member(jsii_name="maskEnd")
    @builtins.classmethod
    def mask_end(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
        length: jsii.Number,
        mask: typing.Optional[builtins.str] = None,
    ) -> ITransform:
        '''
        :param field: -
        :param length: -
        :param mask: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2acd39d37b83d498dba9046e8062304f5227103f50f8d473a9413c6e51236421)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument length", value=length, expected_type=type_hints["length"])
            check_type(argname="argument mask", value=mask, expected_type=type_hints["mask"])
        return typing.cast(ITransform, jsii.sinvoke(cls, "maskEnd", [field, length, mask]))

    @jsii.member(jsii_name="maskStart")
    @builtins.classmethod
    def mask_start(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
        length: jsii.Number,
        mask: typing.Optional[builtins.str] = None,
    ) -> ITransform:
        '''
        :param field: -
        :param length: -
        :param mask: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2550ec4dead61e5b0ae4ece8179540f94ded48f2beb2242305d9d547b7f1070)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument length", value=length, expected_type=type_hints["length"])
            check_type(argname="argument mask", value=mask, expected_type=type_hints["mask"])
        return typing.cast(ITransform, jsii.sinvoke(cls, "maskStart", [field, length, mask]))

    @jsii.member(jsii_name="truncate")
    @builtins.classmethod
    def truncate(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
        length: jsii.Number,
    ) -> ITransform:
        '''(experimental) Truncates the field to a specified length.

        :param field: a source field to truncate.
        :param length: the maximum length after truncation.

        :return: a

        :see: Transform instance
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c32903e226b3cb4c5abb8f003faf20da66d939c849a4e3f6437bfa9f15338d65)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument length", value=length, expected_type=type_hints["length"])
        return typing.cast(ITransform, jsii.sinvoke(cls, "truncate", [field, length]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.TriggerConfig",
    jsii_struct_bases=[],
    name_mapping={"properties": "properties"},
)
class TriggerConfig:
    def __init__(
        self,
        *,
        properties: typing.Optional[typing.Union["TriggerProperties", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param properties: 

        :stability: experimental
        '''
        if isinstance(properties, dict):
            properties = TriggerProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08b0d9faa4910c0e23d0378d533d86a82930a2a943b1df1a232d4069514d2b44)
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def properties(self) -> typing.Optional["TriggerProperties"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional["TriggerProperties"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TriggerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.TriggerProperties",
    jsii_struct_bases=[],
    name_mapping={
        "data_pull_config": "dataPullConfig",
        "schedule": "schedule",
        "flow_error_deactivation_threshold": "flowErrorDeactivationThreshold",
        "properties": "properties",
    },
)
class TriggerProperties:
    def __init__(
        self,
        *,
        data_pull_config: typing.Union[DataPullConfig, typing.Dict[builtins.str, typing.Any]],
        schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
        flow_error_deactivation_threshold: typing.Optional[jsii.Number] = None,
        properties: typing.Optional[typing.Union[ScheduleProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param data_pull_config: 
        :param schedule: 
        :param flow_error_deactivation_threshold: 
        :param properties: 

        :stability: experimental
        '''
        if isinstance(data_pull_config, dict):
            data_pull_config = DataPullConfig(**data_pull_config)
        if isinstance(properties, dict):
            properties = ScheduleProperties(**properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a5595e28b343c24db0c5791c565077bcd1fc6f83d998a876f019a80cc3446ce)
            check_type(argname="argument data_pull_config", value=data_pull_config, expected_type=type_hints["data_pull_config"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument flow_error_deactivation_threshold", value=flow_error_deactivation_threshold, expected_type=type_hints["flow_error_deactivation_threshold"])
            check_type(argname="argument properties", value=properties, expected_type=type_hints["properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "data_pull_config": data_pull_config,
            "schedule": schedule,
        }
        if flow_error_deactivation_threshold is not None:
            self._values["flow_error_deactivation_threshold"] = flow_error_deactivation_threshold
        if properties is not None:
            self._values["properties"] = properties

    @builtins.property
    def data_pull_config(self) -> DataPullConfig:
        '''
        :stability: experimental
        '''
        result = self._values.get("data_pull_config")
        assert result is not None, "Required property 'data_pull_config' is missing"
        return typing.cast(DataPullConfig, result)

    @builtins.property
    def schedule(self) -> _aws_cdk_aws_events_ceddda9d.Schedule:
        '''
        :stability: experimental
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Schedule, result)

    @builtins.property
    def flow_error_deactivation_threshold(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("flow_error_deactivation_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def properties(self) -> typing.Optional[ScheduleProperties]:
        '''
        :stability: experimental
        '''
        result = self._values.get("properties")
        return typing.cast(typing.Optional[ScheduleProperties], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TriggerProperties(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.TriggeredFlowBaseProps",
    jsii_struct_bases=[FlowProps],
    name_mapping={
        "destination": "destination",
        "mappings": "mappings",
        "source": "source",
        "description": "description",
        "filters": "filters",
        "key": "key",
        "name": "name",
        "transforms": "transforms",
        "validations": "validations",
        "auto_activate": "autoActivate",
        "status": "status",
    },
)
class TriggeredFlowBaseProps(FlowProps):
    def __init__(
        self,
        *,
        destination: "IDestination",
        mappings: typing.Sequence["IMapping"],
        source: "ISource",
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence["IFilter"]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
        auto_activate: typing.Optional[builtins.bool] = None,
        status: typing.Optional[FlowStatus] = None,
    ) -> None:
        '''
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 
        :param auto_activate: 
        :param status: (experimental) The status to set on the flow. Use this over {@link autoActivate}.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__881f3c09d75b30ebfa1052386ec4d818fbe77108f41bdb330c146010693f9340)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument transforms", value=transforms, expected_type=type_hints["transforms"])
            check_type(argname="argument validations", value=validations, expected_type=type_hints["validations"])
            check_type(argname="argument auto_activate", value=auto_activate, expected_type=type_hints["auto_activate"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
            "mappings": mappings,
            "source": source,
        }
        if description is not None:
            self._values["description"] = description
        if filters is not None:
            self._values["filters"] = filters
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if transforms is not None:
            self._values["transforms"] = transforms
        if validations is not None:
            self._values["validations"] = validations
        if auto_activate is not None:
            self._values["auto_activate"] = auto_activate
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def destination(self) -> "IDestination":
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("IDestination", result)

    @builtins.property
    def mappings(self) -> typing.List["IMapping"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List["IMapping"], result)

    @builtins.property
    def source(self) -> "ISource":
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("ISource", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List["IFilter"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List["IFilter"]], result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transforms(self) -> typing.Optional[typing.List[ITransform]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("transforms")
        return typing.cast(typing.Optional[typing.List[ITransform]], result)

    @builtins.property
    def validations(self) -> typing.Optional[typing.List[IValidation]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("validations")
        return typing.cast(typing.Optional[typing.List[IValidation]], result)

    @builtins.property
    def auto_activate(self) -> typing.Optional[builtins.bool]:
        '''
        :deprecated: . This property is deprecated and will be removed in a future release. Use {@link status } instead

        :stability: deprecated
        '''
        result = self._values.get("auto_activate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def status(self) -> typing.Optional[FlowStatus]:
        '''(experimental) The status to set on the flow.

        Use this over {@link autoActivate}.

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[FlowStatus], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TriggeredFlowBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IValidation)
class Validation(
    OperationBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.Validation",
):
    '''(experimental) A representation of a validation operation, that is an operation testing records and acting on the test results.

    :stability: experimental
    '''

    def __init__(
        self,
        condition: "ValidationCondition",
        action: "ValidationAction",
    ) -> None:
        '''
        :param condition: -
        :param action: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17d0a7e0c9f7824af925917ebf8638687c5bf11d56459938477e76a6833a4f99)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
        jsii.create(self.__class__, self, [condition, action])

    @jsii.member(jsii_name="when")
    @builtins.classmethod
    def when(
        cls,
        condition: "ValidationCondition",
        action: "ValidationAction",
    ) -> IValidation:
        '''
        :param condition: a.
        :param action: a.

        :return: a Validation instance

        :see: ValidationAction for the validation
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67ca94b43da0f5239fa9d3debb200cfc239bda03c2ab5cb6a652e0f81f7f9ddc)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
        return typing.cast(IValidation, jsii.sinvoke(cls, "when", [condition, action]))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> "ValidationAction":
        '''
        :stability: experimental
        '''
        return typing.cast("ValidationAction", jsii.get(self, "action"))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> "ValidationCondition":
        '''
        :stability: experimental
        '''
        return typing.cast("ValidationCondition", jsii.get(self, "condition"))


class ValidationAction(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ValidationAction",
):
    '''
    :stability: experimental
    '''

    def __init__(self, action: builtins.str) -> None:
        '''
        :param action: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6ab11a20a421606aa4a75efad2710edf490193982d06bdda848e63e5004916e)
            check_type(argname="argument action", value=action, expected_type=type_hints["action"])
        jsii.create(self.__class__, self, [action])

    @jsii.member(jsii_name="ignoreRecord")
    @builtins.classmethod
    def ignore_record(cls) -> "ValidationAction":
        '''
        :return: a

        :see: ValidationAction that removes a record from the flow execution result
        :stability: experimental
        '''
        return typing.cast("ValidationAction", jsii.sinvoke(cls, "ignoreRecord", []))

    @jsii.member(jsii_name="terminateFlow")
    @builtins.classmethod
    def terminate_flow(cls) -> "ValidationAction":
        '''
        :return: a

        :see: ValidationAction that terminates the whole flow execution
        :stability: experimental
        '''
        return typing.cast("ValidationAction", jsii.sinvoke(cls, "terminateFlow", []))

    @builtins.property
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "action"))


class ValidationCondition(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ValidationCondition",
):
    '''(experimental) A representation of a validation condition on a particular field in a flow execution.

    :stability: experimental
    '''

    def __init__(self, field: builtins.str, validation: builtins.str) -> None:
        '''
        :param field: -
        :param validation: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fa951e67892a14eb66e58a134d78cd121a89409ae405b3fc282424907374786)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
            check_type(argname="argument validation", value=validation, expected_type=type_hints["validation"])
        jsii.create(self.__class__, self, [field, validation])

    @jsii.member(jsii_name="isDefault")
    @builtins.classmethod
    def is_default(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    ) -> "ValidationCondition":
        '''
        :param field: a field for which the validation will be performed.

        :return: a

        :see: ValidationCondition instance
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e358a270bee6e0250a4fef9ab13c1d9fd629976d950a828b4c6095617faeb739)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
        return typing.cast("ValidationCondition", jsii.sinvoke(cls, "isDefault", [field]))

    @jsii.member(jsii_name="isNegative")
    @builtins.classmethod
    def is_negative(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    ) -> "ValidationCondition":
        '''(experimental) Validates whether a particular field in an execution is negative.

        :param field: a field for which the validation will be performed.

        :return: a

        :see: ValidationCondition instance
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8660955800816a63c713edf4cedc6b5bd3f8508158ed48f3f1bcb93963ed86ee)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
        return typing.cast("ValidationCondition", jsii.sinvoke(cls, "isNegative", [field]))

    @jsii.member(jsii_name="isNotNull")
    @builtins.classmethod
    def is_not_null(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    ) -> "ValidationCondition":
        '''
        :param field: a field for which the validation will be performed.

        :return: a

        :see: ValidationCondition instance
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ca5f819a7a2769713267e5a06a363b02303fc7a02563ad63b427b398c8b0ce2)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
        return typing.cast("ValidationCondition", jsii.sinvoke(cls, "isNotNull", [field]))

    @jsii.member(jsii_name="isNull")
    @builtins.classmethod
    def is_null(
        cls,
        field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    ) -> "ValidationCondition":
        '''(experimental) Validates whether a particular field has no value.

        :param field: a field for which the validation will be performed.

        :return: a

        :see: ValidationCondition instance
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2367c161e7bef9cf940a0f0d217ab26c89c27654335b8fdf1a4fa4174c76a3ed)
            check_type(argname="argument field", value=field, expected_type=type_hints["field"])
        return typing.cast("ValidationCondition", jsii.sinvoke(cls, "isNull", [field]))

    @builtins.property
    @jsii.member(jsii_name="field")
    def field(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "field"))

    @builtins.property
    @jsii.member(jsii_name="validation")
    def validation(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "validation"))


class WriteOperation(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.WriteOperation",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        type: "WriteOperationType",
        ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param type: -
        :param ids: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73f7b1adeb34e5db29fb94883369e879db3c560d15a3780e96a8395a83c68ae5)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument ids", value=ids, expected_type=type_hints["ids"])
        jsii.create(self.__class__, self, [type, ids])

    @jsii.member(jsii_name="delete")
    @builtins.classmethod
    def delete(
        cls,
        ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "WriteOperation":
        '''
        :param ids: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1615e1c8b7a88521ec7bb5582944e3d891389ab5133988adb27665eb301f8d5)
            check_type(argname="argument ids", value=ids, expected_type=type_hints["ids"])
        return typing.cast("WriteOperation", jsii.sinvoke(cls, "delete", [ids]))

    @jsii.member(jsii_name="insert")
    @builtins.classmethod
    def insert(
        cls,
        ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "WriteOperation":
        '''
        :param ids: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ac64bd6fc67a5fb99235ed0ba6ef9ad8d078a017d9a4fcf2b238594332ddcc1)
            check_type(argname="argument ids", value=ids, expected_type=type_hints["ids"])
        return typing.cast("WriteOperation", jsii.sinvoke(cls, "insert", [ids]))

    @jsii.member(jsii_name="update")
    @builtins.classmethod
    def update(
        cls,
        ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "WriteOperation":
        '''
        :param ids: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3745e4221919777d18492c9ab67350b540cd9a81943c1786bc5a732333892140)
            check_type(argname="argument ids", value=ids, expected_type=type_hints["ids"])
        return typing.cast("WriteOperation", jsii.sinvoke(cls, "update", [ids]))

    @jsii.member(jsii_name="upsert")
    @builtins.classmethod
    def upsert(
        cls,
        ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "WriteOperation":
        '''
        :param ids: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a768fe8cad0fc8d76119bf36b0b0901ed4f1e02a778804c973adea107c099606)
            check_type(argname="argument ids", value=ids, expected_type=type_hints["ids"])
        return typing.cast("WriteOperation", jsii.sinvoke(cls, "upsert", [ids]))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> "WriteOperationType":
        '''
        :stability: experimental
        '''
        return typing.cast("WriteOperationType", jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="ids")
    def ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ids"))


@jsii.enum(jsii_type="@cdklabs/cdk-appflow.WriteOperationType")
class WriteOperationType(enum.Enum):
    '''
    :stability: experimental
    '''

    DELETE = "DELETE"
    '''
    :stability: experimental
    '''
    INSERT = "INSERT"
    '''
    :stability: experimental
    '''
    UPDATE = "UPDATE"
    '''
    :stability: experimental
    '''
    UPSERT = "UPSERT"
    '''
    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ZendeskConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "instance_url": "instanceUrl",
        "o_auth": "oAuth",
    },
)
class ZendeskConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        instance_url: builtins.str,
        o_auth: typing.Union["ZendeskOAuthSettings", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param instance_url: 
        :param o_auth: 

        :stability: experimental
        '''
        if isinstance(o_auth, dict):
            o_auth = ZendeskOAuthSettings(**o_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__793b9e17c548f9557156ccc9f70fad08825c498ddd0d139a291e99df30fa18f0)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument instance_url", value=instance_url, expected_type=type_hints["instance_url"])
            check_type(argname="argument o_auth", value=o_auth, expected_type=type_hints["o_auth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_url": instance_url,
            "o_auth": o_auth,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_url(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("instance_url")
        assert result is not None, "Required property 'instance_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def o_auth(self) -> "ZendeskOAuthSettings":
        '''
        :stability: experimental
        '''
        result = self._values.get("o_auth")
        assert result is not None, "Required property 'o_auth' is missing"
        return typing.cast("ZendeskOAuthSettings", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZendeskConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ZendeskInstanceUrlBuilder(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ZendeskInstanceUrlBuilder",
):
    '''
    :stability: experimental
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="buildFromAccount")
    @builtins.classmethod
    def build_from_account(cls, account: builtins.str) -> builtins.str:
        '''
        :param account: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c702d5690575e12254d4754078c852e743427c9206579bb48a06e3969a46b9f7)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "buildFromAccount", [account]))


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ZendeskOAuthSettings",
    jsii_struct_bases=[],
    name_mapping={
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "access_token": "accessToken",
    },
)
class ZendeskOAuthSettings:
    def __init__(
        self,
        *,
        client_id: _aws_cdk_ceddda9d.SecretValue,
        client_secret: _aws_cdk_ceddda9d.SecretValue,
        access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param client_id: 
        :param client_secret: 
        :param access_token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85f74bf49c07fa8e80d2caf3ebf8f612482134e20074260644582a8666e89eb7)
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument access_token", value=access_token, expected_type=type_hints["access_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if access_token is not None:
            self._values["access_token"] = access_token

    @builtins.property
    def client_id(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_id")
        assert result is not None, "Required property 'client_id' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def client_secret(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("client_secret")
        assert result is not None, "Required property 'client_secret' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def access_token(self) -> typing.Optional[_aws_cdk_ceddda9d.SecretValue]:
        '''
        :stability: experimental
        '''
        result = self._values.get("access_token")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.SecretValue], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZendeskOAuthSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.ZendeskSourceProps",
    jsii_struct_bases=[],
    name_mapping={
        "object": "object",
        "profile": "profile",
        "api_version": "apiVersion",
    },
)
class ZendeskSourceProps:
    def __init__(
        self,
        *,
        object: builtins.str,
        profile: "ZendeskConnectorProfile",
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12d6ac01e1819517b8f5ade63157f0ddc52a9c21ef9ffb1337daaf1d72b859b4)
            check_type(argname="argument object", value=object, expected_type=type_hints["object"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument api_version", value=api_version, expected_type=type_hints["api_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "object": object,
            "profile": profile,
        }
        if api_version is not None:
            self._values["api_version"] = api_version

    @builtins.property
    def object(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        result = self._values.get("object")
        assert result is not None, "Required property 'object' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def profile(self) -> "ZendeskConnectorProfile":
        '''
        :stability: experimental
        '''
        result = self._values.get("profile")
        assert result is not None, "Required property 'profile' is missing"
        return typing.cast("ZendeskConnectorProfile", result)

    @builtins.property
    def api_version(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("api_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ZendeskSourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.AmazonRdsForPostgreSqlConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={
        "key": "key",
        "name": "name",
        "basic_auth": "basicAuth",
        "database": "database",
        "hostname": "hostname",
        "port": "port",
    },
)
class AmazonRdsForPostgreSqlConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        basic_auth: typing.Union[AmazonRdsForPostgreSqlBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
        database: builtins.str,
        hostname: builtins.str,
        port: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties of the AmazonRdsForPostgreSqlConnectorProfile.

        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param basic_auth: (experimental) The auth settings for the profile.
        :param database: (experimental) The name of the PostgreSQL database.
        :param hostname: (experimental) The PostgreSQL hostname.
        :param port: (experimental) The PostgreSQL communication port.

        :stability: experimental
        '''
        if isinstance(basic_auth, dict):
            basic_auth = AmazonRdsForPostgreSqlBasicAuthSettings(**basic_auth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06579ce6121216cc8ffcacfabfa42d87b49a8b42d2f2dd0d6bf18a19940a8c77)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument basic_auth", value=basic_auth, expected_type=type_hints["basic_auth"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "basic_auth": basic_auth,
            "database": database,
            "hostname": hostname,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def basic_auth(self) -> AmazonRdsForPostgreSqlBasicAuthSettings:
        '''(experimental) The auth settings for the profile.

        :stability: experimental
        '''
        result = self._values.get("basic_auth")
        assert result is not None, "Required property 'basic_auth' is missing"
        return typing.cast(AmazonRdsForPostgreSqlBasicAuthSettings, result)

    @builtins.property
    def database(self) -> builtins.str:
        '''(experimental) The name of the PostgreSQL database.

        :stability: experimental
        '''
        result = self._values.get("database")
        assert result is not None, "Required property 'database' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hostname(self) -> builtins.str:
        '''(experimental) The PostgreSQL hostname.

        :stability: experimental
        '''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The PostgreSQL communication port.

        :stability: experimental
        '''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AmazonRdsForPostgreSqlConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.AsanaConnectorProfileProps",
    jsii_struct_bases=[ConnectorProfileProps],
    name_mapping={"key": "key", "name": "name", "pat_token": "patToken"},
)
class AsanaConnectorProfileProps(ConnectorProfileProps):
    def __init__(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        pat_token: _aws_cdk_ceddda9d.SecretValue,
    ) -> None:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 
        :param pat_token: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89b05a676f3a85bf2b6f7814749de8f4991e610d071aed5d693f8a732d12d900)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument pat_token", value=pat_token, expected_type=type_hints["pat_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "pat_token": pat_token,
        }
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) TODO: think if this should be here as not all connector profiles have that.

        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pat_token(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''
        :stability: experimental
        '''
        result = self._values.get("pat_token")
        assert result is not None, "Required property 'pat_token' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AsanaConnectorProfileProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IConnectorProfile)
class ConnectorProfileBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-appflow.ConnectorProfileBase",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: typing.Union[ConnectorProfileProps, typing.Dict[builtins.str, typing.Any]],
        connector_type: ConnectorType,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        :param connector_type: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f41824d4d0e7e596b73b8964ae3c9323e7ac9e57fc2490edce69fc33b58e525)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
            check_type(argname="argument connector_type", value=connector_type, expected_type=type_hints["connector_type"])
        jsii.create(self.__class__, self, [scope, id, props, connector_type])

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    @abc.abstractmethod
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    @abc.abstractmethod
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="tryAddNodeDependency")
    def _try_add_node_dependency(
        self,
        scope: _constructs_77d1e7e8.IConstruct,
        resource: typing.Optional[typing.Union[builtins.str, _constructs_77d1e7e8.IConstruct]] = None,
    ) -> None:
        '''
        :param scope: -
        :param resource: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88ce195d30a4f9a428558674e3292dbaa455820c183acaffd9afb1e9718e87ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument resource", value=resource, expected_type=type_hints["resource"])
        return typing.cast(None, jsii.invoke(self, "tryAddNodeDependency", [scope, resource]))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''
        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''
        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], jsii.get(self, "credentials"))


class _ConnectorProfileBaseProxy(
    ConnectorProfileBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, ConnectorProfileBase).__jsii_proxy_class__ = lambda : _ConnectorProfileBaseProxy


@jsii.implements(IFlow)
class FlowBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-appflow.FlowBase",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        type: FlowType,
        status: typing.Optional[FlowStatus] = None,
        trigger_config: typing.Optional[typing.Union[TriggerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        destination: "IDestination",
        mappings: typing.Sequence["IMapping"],
        source: "ISource",
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence["IFilter"]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param type: 
        :param status: 
        :param trigger_config: 
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b56531af8c41eed5beccf6a33a61319cd682a85bbf2967c237fc17d06f31a5d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FlowBaseProps(
            type=type,
            status=status,
            trigger_config=trigger_config,
            destination=destination,
            mappings=mappings,
            source=source,
            description=description,
            filters=filters,
            key=key,
            name=name,
            transforms=transforms,
            validations=validations,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''
        :param metric_name: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f3c65eebc4f29cf16125ffb6702a331f9a79ae1812e08301259b59c02859425)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, options]))

    @jsii.member(jsii_name="metricFlowExecutionRecordsProcessed")
    def metric_flow_execution_records_processed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of records that Amazon AppFlow attempted to transfer for the flow run.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionRecordsProcessed", [options]))

    @jsii.member(jsii_name="metricFlowExecutionsFailed")
    def metric_flow_executions_failed(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of failed flow runs.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionsFailed", [options]))

    @jsii.member(jsii_name="metricFlowExecutionsStarted")
    def metric_flow_executions_started(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of flow runs started.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionsStarted", [options]))

    @jsii.member(jsii_name="metricFlowExecutionsSucceeded")
    def metric_flow_executions_succeeded(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the number of successful flow runs.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionsSucceeded", [options]))

    @jsii.member(jsii_name="metricFlowExecutionTime")
    def metric_flow_execution_time(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a metric to report the  interval, in milliseconds, between the time the flow starts and the time it finishes.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        options = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricFlowExecutionTime", [options]))

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2acf34eacdae40710a13c3ed45f83158f59e3e15966b80313d67d608ba9ee3a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onEvent", [id, options]))

    @jsii.member(jsii_name="onRunCompleted")
    def on_run_completed(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f03f9a11b1059cab6d66afc004104a59693f30bd1d46f2cbc04ed46840517563)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onRunCompleted", [id, options]))

    @jsii.member(jsii_name="onRunStarted")
    def on_run_started(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__898943b33b4140f7380992a94ce5f3f39a5d95bf03491505dc4cb95af4a7de3e)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onRunStarted", [id, options]))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        '''(experimental) The ARN of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the flow.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> FlowType:
        '''(experimental) The type of the flow.

        :stability: experimental
        '''
        return typing.cast(FlowType, jsii.get(self, "type"))


class _FlowBaseProxy(
    FlowBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, FlowBase).__jsii_proxy_class__ = lambda : _FlowBaseProxy


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.FlowBaseProps",
    jsii_struct_bases=[FlowProps],
    name_mapping={
        "destination": "destination",
        "mappings": "mappings",
        "source": "source",
        "description": "description",
        "filters": "filters",
        "key": "key",
        "name": "name",
        "transforms": "transforms",
        "validations": "validations",
        "type": "type",
        "status": "status",
        "trigger_config": "triggerConfig",
    },
)
class FlowBaseProps(FlowProps):
    def __init__(
        self,
        *,
        destination: "IDestination",
        mappings: typing.Sequence["IMapping"],
        source: "ISource",
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence["IFilter"]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
        type: FlowType,
        status: typing.Optional[FlowStatus] = None,
        trigger_config: typing.Optional[typing.Union[TriggerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 
        :param type: 
        :param status: 
        :param trigger_config: 

        :stability: experimental
        '''
        if isinstance(trigger_config, dict):
            trigger_config = TriggerConfig(**trigger_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35de0ceeba864e70ecbbe43f5c1d7bece48df28eda3b3a6792c125eaa4810523)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument transforms", value=transforms, expected_type=type_hints["transforms"])
            check_type(argname="argument validations", value=validations, expected_type=type_hints["validations"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument trigger_config", value=trigger_config, expected_type=type_hints["trigger_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
            "mappings": mappings,
            "source": source,
            "type": type,
        }
        if description is not None:
            self._values["description"] = description
        if filters is not None:
            self._values["filters"] = filters
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if transforms is not None:
            self._values["transforms"] = transforms
        if validations is not None:
            self._values["validations"] = validations
        if status is not None:
            self._values["status"] = status
        if trigger_config is not None:
            self._values["trigger_config"] = trigger_config

    @builtins.property
    def destination(self) -> "IDestination":
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast("IDestination", result)

    @builtins.property
    def mappings(self) -> typing.List["IMapping"]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List["IMapping"], result)

    @builtins.property
    def source(self) -> "ISource":
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("ISource", result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List["IFilter"]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List["IFilter"]], result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transforms(self) -> typing.Optional[typing.List[ITransform]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("transforms")
        return typing.cast(typing.Optional[typing.List[ITransform]], result)

    @builtins.property
    def validations(self) -> typing.Optional[typing.List[IValidation]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("validations")
        return typing.cast(typing.Optional[typing.List[IValidation]], result)

    @builtins.property
    def type(self) -> FlowType:
        '''
        :stability: experimental
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(FlowType, result)

    @builtins.property
    def status(self) -> typing.Optional[FlowStatus]:
        '''
        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[FlowStatus], result)

    @builtins.property
    def trigger_config(self) -> typing.Optional[TriggerConfig]:
        '''
        :stability: experimental
        '''
        result = self._values.get("trigger_config")
        return typing.cast(typing.Optional[TriggerConfig], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FlowBaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GitHubConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GitHubConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        basic_auth: typing.Optional[typing.Union[GitHubBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        o_auth: typing.Optional[typing.Union[GitHubOAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param basic_auth: 
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f9e401efb1d1cbb7beb077ff01c665cdd93baa94ed7115889fb572273e3f077)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GitHubConnectorProfileProps(
            basic_auth=basic_auth, o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "GitHubConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d92d1f337d55056eee44e5cb4fc8d5f572fb6f21a410c420029a743dfde292e8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("GitHubConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "GitHubConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__024d255b0faaeb3d18d0d1d30c2700693bab2b18eee0319a5fd82f6e0bd134ab)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("GitHubConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


class GoogleAdsConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_version: builtins.str,
        developer_token: _aws_cdk_ceddda9d.SecretValue,
        o_auth: typing.Union[GoogleAdsOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        manager_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_version: 
        :param developer_token: 
        :param o_auth: 
        :param manager_id: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f86afff4e70e3f5322709dd23ddff9112e2c6439819db87fb1570f05121e4ae7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GoogleAdsConnectorProfileProps(
            api_version=api_version,
            developer_token=developer_token,
            o_auth=o_auth,
            manager_id=manager_id,
            key=key,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "GoogleAdsConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5886bd104fbcfbee5a5e13271dc65eba692c4b203fd7e3b57dd534758876df5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("GoogleAdsConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "GoogleAdsConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd36306e21ad794d3ad49d35c157d4d1c59dabbe31a3d5d925442192131c8fc9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("GoogleAdsConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


class GoogleAnalytics4ConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4ConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        o_auth: typing.Union[GoogleAnalytics4OAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c43bd6b69bc3bf59de5b391f25cdf12b469de365ed8de5be512e17a271f7045)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GoogleAnalytics4ConnectorProfileProps(
            o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "GoogleAnalytics4ConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__637fbb37964ed107f6b98fa3a2364d0015e3f062ded5c0ed3cdbd4b1f9d2bce4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("GoogleAnalytics4ConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "GoogleAnalytics4ConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eafc7f7b62ebd94da254cb5bcd21396d7915c304471032e3ada0d238287b38d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("GoogleAnalytics4ConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


class GoogleBigQueryConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQueryConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        o_auth: typing.Union[GoogleBigQueryOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea31aa0261671f54af7beec877efbbf33709316e870e74cca3c7de97b6da90e9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = GoogleBigQueryConnectorProfileProps(o_auth=o_auth, key=key, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "GoogleBigQueryConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34bd60074077ce74fb7dfee3d50fc4565c5c9a4944714c75ec6b392fd46705b0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("GoogleBigQueryConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "GoogleBigQueryConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9f13077418355c76fb5cfa27ee04588c7082264956de751c0d05bdf9038224)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("GoogleBigQueryConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


class HubSpotConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.HubSpotConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        o_auth: typing.Union[HubSpotOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f2136d4559db32f0e5755749dec96f0202761cc14f7e5dd4c10f5c2c5fc15aa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = HubSpotConnectorProfileProps(o_auth=o_auth, key=key, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "HubSpotConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0319dd9c8a5d2e3bee2c855238214cb1a8f4a38b759b49f5fe258829cc35aa3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("HubSpotConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "HubSpotConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14884df6d2e23cdfeecd9992ccb92d81f2dfcf150f24e3d572fd294238c3fe83)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("HubSpotConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IDestination")
class IDestination(IVertex, typing_extensions.Protocol):
    '''(experimental) A destination of an AppFlow flow.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        ...


class _IDestinationProxy(
    jsii.proxy_for(IVertex), # type: ignore[misc]
):
    '''(experimental) A destination of an AppFlow flow.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IDestination"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__763c41122983019c457da20c45fe1dfbbca1c1449cc69b4c8b816e2a90d82e4d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDestination).__jsii_proxy_class__ = lambda : _IDestinationProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IFilter")
class IFilter(IOperation, typing_extensions.Protocol):
    '''(experimental) A representation of a mapping operation, that is an operation filtering records at the source.

    :stability: experimental
    '''

    pass


class _IFilterProxy(
    jsii.proxy_for(IOperation), # type: ignore[misc]
):
    '''(experimental) A representation of a mapping operation, that is an operation filtering records at the source.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IFilter"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IFilter).__jsii_proxy_class__ = lambda : _IFilterProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.IMapping")
class IMapping(IOperation, typing_extensions.Protocol):
    '''(experimental) A representation of a mapping operation, that is an operation translating source to destination fields.

    :stability: experimental
    '''

    pass


class _IMappingProxy(
    jsii.proxy_for(IOperation), # type: ignore[misc]
):
    '''(experimental) A representation of a mapping operation, that is an operation translating source to destination fields.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.IMapping"
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMapping).__jsii_proxy_class__ = lambda : _IMappingProxy


@jsii.interface(jsii_type="@cdklabs/cdk-appflow.ISource")
class ISource(IVertex, typing_extensions.Protocol):
    '''(experimental) A source of an AppFlow flow.

    :stability: experimental
    '''

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        ...


class _ISourceProxy(
    jsii.proxy_for(IVertex), # type: ignore[misc]
):
    '''(experimental) A source of an AppFlow flow.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@cdklabs/cdk-appflow.ISource"

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0164bc87a394237879abd8ee65e72956a291ed0eea1cc44de9736e00403baf94)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISource).__jsii_proxy_class__ = lambda : _ISourceProxy


class JdbcSmallDataScaleConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.JdbcSmallDataScaleConnectorProfile",
):
    '''(experimental) The connector profile for the JDBC connector.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        basic_auth: typing.Union[JdbcSmallDataScaleBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
        database: builtins.str,
        driver: JdbcDriver,
        hostname: builtins.str,
        port: jsii.Number,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a new instance of the JdbcSmallDataScaleConnectorProfile.

        :param scope: the Construct scope for this connector profile.
        :param id: the id of this connector profile.
        :param basic_auth: (experimental) The auth settings for the profile.
        :param database: (experimental) The name of the database.
        :param driver: (experimental) The driver for the database. Effectively specifies the type of database.
        :param hostname: (experimental) The hostname of the database to interact with.
        :param port: (experimental) The database communication port.
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e32deb023fd1da8653ae939d2fc08254ee0ded96f4e39571b669df7c596e4a01)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = JdbcSmallDataScaleConnectorProfileProps(
            basic_auth=basic_auth,
            database=database,
            driver=driver,
            hostname=hostname,
            port=port,
            key=key,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "JdbcSmallDataScaleConnectorProfile":
        '''(experimental) Imports an existing JdbcSmallDataScaleConnectorProfile.

        :param scope: the scope for the connector profile.
        :param id: the connector profile's ID.
        :param arn: the ARN for the existing connector profile.

        :return: An instance of the JdbcSmallDataScaleConnectorProfile

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdead6c1e387618dbc67702ba3c746da0fd7d293156ff0daec657685e2f61dd9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("JdbcSmallDataScaleConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "JdbcSmallDataScaleConnectorProfile":
        '''(experimental) Imports an existing JdbcSmallDataScaleConnectorProfile.

        :param scope: the scope for the connector profile.
        :param id: the connector profile's ID.
        :param name: the name for the existing connector profile.

        :return: An instance of the JdbcSmallDataScaleConnectorProfile

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc97d291eeff1c6c890723e428dd35fda34ec527efa1cdd1e7b2b2ca04bfb706)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("JdbcSmallDataScaleConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        _props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [_props]))


@jsii.implements(ISource)
class JdbcSmallDataScaleSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.JdbcSmallDataScaleSource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: typing.Union[JdbcSmallDataScaleObject, typing.Dict[builtins.str, typing.Any]],
        profile: JdbcSmallDataScaleConnectorProfile,
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        props = JdbcSmallDataScaleSourceProps(
            object=object, profile=profile, api_version=api_version
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17c85e4f48690fbb00d1604ff53a4fedbdbe8249687c1ef7c84e32fd1685bb2b)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class MailchimpConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MailchimpConnectorProfile",
):
    '''(experimental) A class that represents a Mailchimp Connector Profile.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        api_key: _aws_cdk_ceddda9d.SecretValue,
        instance_url: builtins.str,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_key: 
        :param instance_url: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de9b2b10ed2a04588baf16c32519a05254225651f4c460d9c5e32f6fb697d829)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MailchimpConnectorProfileProps(
            api_key=api_key, instance_url=instance_url, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "MailchimpConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fab62bc82e71cddf5bdb22f9430f2124a811b6af45e84d43ee08202bbd6631a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("MailchimpConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "MailchimpConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__065bdf7524e5dbd428b95d00e42375bf860b0486f0995251e8b669ec6ac9c3c6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MailchimpConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class MailchimpSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MailchimpSource",
):
    '''(experimental) A class that represents a Mailchimp v3 Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: MailchimpConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = MailchimpSourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a299aad732300797f33efd78c0a733afbf3e2e4abbd46ee3cc8968e60fc1712)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IMapping)
class Mapping(
    OperationBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.Mapping",
):
    '''(experimental) A representation of an instance of a mapping operation, that is an operation translating source to destination fields.

    :stability: experimental
    '''

    def __init__(self, tasks: typing.Sequence[ITask]) -> None:
        '''
        :param tasks: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a678dcca6d941420e56a333102b5a0cb8c0d803561d5d835f4240c199f4ac4)
            check_type(argname="argument tasks", value=tasks, expected_type=type_hints["tasks"])
        jsii.create(self.__class__, self, [tasks])

    @jsii.member(jsii_name="add")
    @builtins.classmethod
    def add(
        cls,
        source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        *,
        name: builtins.str,
        data_type: typing.Optional[builtins.str] = None,
    ) -> "Mapping":
        '''(experimental) Specifies an addition mapping of two numeric values from asource to a destination.

        :param source_field1: a numeric value.
        :param source_field2: a numeric value.
        :param name: 
        :param data_type: 

        :return: an IMapping instance

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__630b751d36137c5140a0419a292ad559adbdbce0d246c34f18852346385b0037)
            check_type(argname="argument source_field1", value=source_field1, expected_type=type_hints["source_field1"])
            check_type(argname="argument source_field2", value=source_field2, expected_type=type_hints["source_field2"])
        to = Field(name=name, data_type=data_type)

        return typing.cast("Mapping", jsii.sinvoke(cls, "add", [source_field1, source_field2, to]))

    @jsii.member(jsii_name="concat")
    @builtins.classmethod
    def concat(
        cls,
        from_: typing.Sequence[typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
        to: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        format: builtins.str,
    ) -> "Mapping":
        '''(experimental) A mapping definition building concatenation of source fields into a destination field.

        :param from_: an array of source fields.
        :param to: a desintation field.
        :param format: a format.

        :return: a mapping instance with concatenation definition

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07c247ea317fe5c6eb58ff91f5ca6af9502cac12e56792a5520cbfc4c32c9906)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument to", value=to, expected_type=type_hints["to"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
        return typing.cast("Mapping", jsii.sinvoke(cls, "concat", [from_, to, format]))

    @jsii.member(jsii_name="divide")
    @builtins.classmethod
    def divide(
        cls,
        source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        *,
        name: builtins.str,
        data_type: typing.Optional[builtins.str] = None,
    ) -> "Mapping":
        '''(experimental) Specifies a division mapping of two numeric values from a source to a destination.

        :param source_field1: a numeric value.
        :param source_field2: a numeric value.
        :param name: 
        :param data_type: 

        :return: an IMapping instance

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05f84f4f0f748a86f5d549f6eac81d409450ea2ef0c46d42e725684c6af1e306)
            check_type(argname="argument source_field1", value=source_field1, expected_type=type_hints["source_field1"])
            check_type(argname="argument source_field2", value=source_field2, expected_type=type_hints["source_field2"])
        to = Field(name=name, data_type=data_type)

        return typing.cast("Mapping", jsii.sinvoke(cls, "divide", [source_field1, source_field2, to]))

    @jsii.member(jsii_name="map")
    @builtins.classmethod
    def map(
        cls,
        from_: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        *,
        name: builtins.str,
        data_type: typing.Optional[builtins.str] = None,
    ) -> IMapping:
        '''
        :param from_: -
        :param name: 
        :param data_type: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebd0fbf617c72b22af5dfe5b02f0f6887532b0c433b7f704339b58b5d6a7ae0c)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
        to = Field(name=name, data_type=data_type)

        return typing.cast(IMapping, jsii.sinvoke(cls, "map", [from_, to]))

    @jsii.member(jsii_name="mapAll")
    @builtins.classmethod
    def map_all(cls, *, exclude: typing.Sequence[builtins.str]) -> IMapping:
        '''
        :param exclude: 

        :stability: experimental
        '''
        config = MapAllConfig(exclude=exclude)

        return typing.cast(IMapping, jsii.sinvoke(cls, "mapAll", [config]))

    @jsii.member(jsii_name="multiply")
    @builtins.classmethod
    def multiply(
        cls,
        source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        *,
        name: builtins.str,
        data_type: typing.Optional[builtins.str] = None,
    ) -> "Mapping":
        '''(experimental) Specifies a multiplication mapping of two numeric values from a source to a destination.

        :param source_field1: a numeric value.
        :param source_field2: a numeric value.
        :param name: 
        :param data_type: 

        :return: an IMapping instance

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bf1b53973e5a4d28322754dfc146a010b77fd30692723b8a3d783a96a654674)
            check_type(argname="argument source_field1", value=source_field1, expected_type=type_hints["source_field1"])
            check_type(argname="argument source_field2", value=source_field2, expected_type=type_hints["source_field2"])
        to = Field(name=name, data_type=data_type)

        return typing.cast("Mapping", jsii.sinvoke(cls, "multiply", [source_field1, source_field2, to]))

    @jsii.member(jsii_name="subtract")
    @builtins.classmethod
    def subtract(
        cls,
        source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
        *,
        name: builtins.str,
        data_type: typing.Optional[builtins.str] = None,
    ) -> "Mapping":
        '''(experimental) Specifies a subtraction mapping of two numeric values from a source to a destination.

        :param source_field1: a numeric value.
        :param source_field2: a numeric value.
        :param name: 
        :param data_type: 

        :return: an IMapping instance

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bf0b9669a6a99c327db9986a7b753319745c897c65990576a333bf3f9577239)
            check_type(argname="argument source_field1", value=source_field1, expected_type=type_hints["source_field1"])
            check_type(argname="argument source_field2", value=source_field2, expected_type=type_hints["source_field2"])
        to = Field(name=name, data_type=data_type)

        return typing.cast("Mapping", jsii.sinvoke(cls, "subtract", [source_field1, source_field2, to]))


class MarketoConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MarketoConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_url: builtins.str,
        o_auth: typing.Union[MarketoOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_url: 
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5374e74f303d3b208f61404b21a2141f422ebc73c4c55c1c0bb9d56dca830409)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MarketoConnectorProfileProps(
            instance_url=instance_url, o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "MarketoConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6719326a52f679caeaf4ee763bcdf20b57cc3721fec1de6baeb25dbd6e04cedc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("MarketoConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "MarketoConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__751aa592c50e735ef9492028fdd783baf185fdd81dae3a88fa20ac5a43ffda41)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MarketoConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class MarketoSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MarketoSource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        profile: MarketoConnectorProfile,
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        props = MarketoSourceProps(
            object=object, profile=profile, api_version=api_version
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d526fba10eba772302583964eed0ad031f9fc46796a3930b26ee72d6f7354e64)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class MicrosoftDynamics365ConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365ConnectorProfile",
):
    '''(experimental) A class that represents a Microsoft Dynamics 365 Connector Profile.

    This connector profile allows to transfer document libraries residing on a Microsoft Dynamics 365's site to Amazon S3.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_url: builtins.str,
        o_auth: typing.Union[MicrosoftDynamics365OAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_url: 
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0bb0eefccf75f7bb468f88528c6c7c0c3cfa07f29f4a753c32612c5e663b09d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MicrosoftDynamics365ConnectorProfileProps(
            instance_url=instance_url, o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "MicrosoftDynamics365ConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95f695492e2672da02edd0d068b199a21c837fdb72221a49705e0813d22f4285)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("MicrosoftDynamics365ConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "MicrosoftDynamics365ConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d547be811c4253a9a7e978e6ed046e654cd132030758eeba17df89bab759499)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MicrosoftDynamics365ConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class MicrosoftDynamics365Source(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MicrosoftDynamics365Source",
):
    '''(experimental) A class that represents a Microsoft Dynamics 365 Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: MicrosoftDynamics365ConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = MicrosoftDynamics365SourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ee08ed5ce759617974eb4dc1e5a90ddf403380044aa2a667eee9212b5da103)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class MicrosoftSharepointOnlineConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineConnectorProfile",
):
    '''(experimental) A class that represents a Microsoft Sharepoint Online Connector Profile.

    This connector profile allows to transfer document libraries residing on a Microsoft Sharepoint Online's site to Amazon S3.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        o_auth: typing.Union[MicrosoftSharepointOnlineOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e8e4b0913b75c925eb456a841b29ed60151ccce3d9dad6b2c9cd15845a6268a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MicrosoftSharepointOnlineConnectorProfileProps(
            o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "MicrosoftSharepointOnlineConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03b3073f8f9e06a602e324649deab60e7b7dd73a8d582c81d4515d58a0e7e191)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("MicrosoftSharepointOnlineConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "MicrosoftSharepointOnlineConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76c71d094d3248d78f6f3e713946ba72ca8b0809bf263a4154c236b53cc3e41e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("MicrosoftSharepointOnlineConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class MicrosoftSharepointOnlineSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.MicrosoftSharepointOnlineSource",
):
    '''(experimental) A class that represents a Microsoft Sharepoint Online Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: typing.Union[MicrosoftSharepointOnlineObject, typing.Dict[builtins.str, typing.Any]],
        profile: MicrosoftSharepointOnlineConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = MicrosoftSharepointOnlineSourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c759b75072354d63580102008aa08f507d648d1438edd61d1dd8c93bda750d2d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IFlow)
class OnDemandFlow(
    FlowBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.OnDemandFlow",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        destination: IDestination,
        mappings: typing.Sequence[IMapping],
        source: ISource,
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence[IFilter]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdd05f239f7e2082c835f28f1395f4cd46f69d24e3fc862cd99eddfd8bf951b6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OnDemandFlowProps(
            destination=destination,
            mappings=mappings,
            source=source,
            description=description,
            filters=filters,
            key=key,
            name=name,
            transforms=transforms,
            validations=validations,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.OnEventFlowProps",
    jsii_struct_bases=[TriggeredFlowBaseProps],
    name_mapping={
        "destination": "destination",
        "mappings": "mappings",
        "source": "source",
        "description": "description",
        "filters": "filters",
        "key": "key",
        "name": "name",
        "transforms": "transforms",
        "validations": "validations",
        "auto_activate": "autoActivate",
        "status": "status",
    },
)
class OnEventFlowProps(TriggeredFlowBaseProps):
    def __init__(
        self,
        *,
        destination: IDestination,
        mappings: typing.Sequence[IMapping],
        source: ISource,
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence[IFilter]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
        auto_activate: typing.Optional[builtins.bool] = None,
        status: typing.Optional[FlowStatus] = None,
    ) -> None:
        '''
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 
        :param auto_activate: 
        :param status: (experimental) The status to set on the flow. Use this over {@link autoActivate}.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3de51d773e1730010fdf7bfeffbbc6e0aa2ec00de7959b616230568433da3b3d)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument transforms", value=transforms, expected_type=type_hints["transforms"])
            check_type(argname="argument validations", value=validations, expected_type=type_hints["validations"])
            check_type(argname="argument auto_activate", value=auto_activate, expected_type=type_hints["auto_activate"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
            "mappings": mappings,
            "source": source,
        }
        if description is not None:
            self._values["description"] = description
        if filters is not None:
            self._values["filters"] = filters
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if transforms is not None:
            self._values["transforms"] = transforms
        if validations is not None:
            self._values["validations"] = validations
        if auto_activate is not None:
            self._values["auto_activate"] = auto_activate
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def destination(self) -> IDestination:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(IDestination, result)

    @builtins.property
    def mappings(self) -> typing.List[IMapping]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List[IMapping], result)

    @builtins.property
    def source(self) -> ISource:
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(ISource, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List[IFilter]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List[IFilter]], result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transforms(self) -> typing.Optional[typing.List[ITransform]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("transforms")
        return typing.cast(typing.Optional[typing.List[ITransform]], result)

    @builtins.property
    def validations(self) -> typing.Optional[typing.List[IValidation]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("validations")
        return typing.cast(typing.Optional[typing.List[IValidation]], result)

    @builtins.property
    def auto_activate(self) -> typing.Optional[builtins.bool]:
        '''
        :deprecated: . This property is deprecated and will be removed in a future release. Use {@link status } instead

        :stability: deprecated
        '''
        result = self._values.get("auto_activate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def status(self) -> typing.Optional[FlowStatus]:
        '''(experimental) The status to set on the flow.

        Use this over {@link autoActivate}.

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[FlowStatus], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnEventFlowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-appflow.OnScheduleFlowProps",
    jsii_struct_bases=[TriggeredFlowBaseProps],
    name_mapping={
        "destination": "destination",
        "mappings": "mappings",
        "source": "source",
        "description": "description",
        "filters": "filters",
        "key": "key",
        "name": "name",
        "transforms": "transforms",
        "validations": "validations",
        "auto_activate": "autoActivate",
        "status": "status",
        "pull_config": "pullConfig",
        "schedule": "schedule",
        "schedule_properties": "scheduleProperties",
    },
)
class OnScheduleFlowProps(TriggeredFlowBaseProps):
    def __init__(
        self,
        *,
        destination: IDestination,
        mappings: typing.Sequence[IMapping],
        source: ISource,
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence[IFilter]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
        auto_activate: typing.Optional[builtins.bool] = None,
        status: typing.Optional[FlowStatus] = None,
        pull_config: typing.Union[DataPullConfig, typing.Dict[builtins.str, typing.Any]],
        schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
        schedule_properties: typing.Optional[typing.Union[ScheduleProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 
        :param auto_activate: 
        :param status: (experimental) The status to set on the flow. Use this over {@link autoActivate}.
        :param pull_config: 
        :param schedule: 
        :param schedule_properties: 

        :stability: experimental
        '''
        if isinstance(pull_config, dict):
            pull_config = DataPullConfig(**pull_config)
        if isinstance(schedule_properties, dict):
            schedule_properties = ScheduleProperties(**schedule_properties)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d3b83aa54f4b21125bcd8395900d743242af7f296f98624a1512d760b575410)
            check_type(argname="argument destination", value=destination, expected_type=type_hints["destination"])
            check_type(argname="argument mappings", value=mappings, expected_type=type_hints["mappings"])
            check_type(argname="argument source", value=source, expected_type=type_hints["source"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument filters", value=filters, expected_type=type_hints["filters"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument transforms", value=transforms, expected_type=type_hints["transforms"])
            check_type(argname="argument validations", value=validations, expected_type=type_hints["validations"])
            check_type(argname="argument auto_activate", value=auto_activate, expected_type=type_hints["auto_activate"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument pull_config", value=pull_config, expected_type=type_hints["pull_config"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument schedule_properties", value=schedule_properties, expected_type=type_hints["schedule_properties"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "destination": destination,
            "mappings": mappings,
            "source": source,
            "pull_config": pull_config,
            "schedule": schedule,
        }
        if description is not None:
            self._values["description"] = description
        if filters is not None:
            self._values["filters"] = filters
        if key is not None:
            self._values["key"] = key
        if name is not None:
            self._values["name"] = name
        if transforms is not None:
            self._values["transforms"] = transforms
        if validations is not None:
            self._values["validations"] = validations
        if auto_activate is not None:
            self._values["auto_activate"] = auto_activate
        if status is not None:
            self._values["status"] = status
        if schedule_properties is not None:
            self._values["schedule_properties"] = schedule_properties

    @builtins.property
    def destination(self) -> IDestination:
        '''
        :stability: experimental
        '''
        result = self._values.get("destination")
        assert result is not None, "Required property 'destination' is missing"
        return typing.cast(IDestination, result)

    @builtins.property
    def mappings(self) -> typing.List[IMapping]:
        '''
        :stability: experimental
        '''
        result = self._values.get("mappings")
        assert result is not None, "Required property 'mappings' is missing"
        return typing.cast(typing.List[IMapping], result)

    @builtins.property
    def source(self) -> ISource:
        '''
        :stability: experimental
        '''
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast(ISource, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def filters(self) -> typing.Optional[typing.List[IFilter]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("filters")
        return typing.cast(typing.Optional[typing.List[IFilter]], result)

    @builtins.property
    def key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''
        :stability: experimental
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''
        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transforms(self) -> typing.Optional[typing.List[ITransform]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("transforms")
        return typing.cast(typing.Optional[typing.List[ITransform]], result)

    @builtins.property
    def validations(self) -> typing.Optional[typing.List[IValidation]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("validations")
        return typing.cast(typing.Optional[typing.List[IValidation]], result)

    @builtins.property
    def auto_activate(self) -> typing.Optional[builtins.bool]:
        '''
        :deprecated: . This property is deprecated and will be removed in a future release. Use {@link status } instead

        :stability: deprecated
        '''
        result = self._values.get("auto_activate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def status(self) -> typing.Optional[FlowStatus]:
        '''(experimental) The status to set on the flow.

        Use this over {@link autoActivate}.

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[FlowStatus], result)

    @builtins.property
    def pull_config(self) -> DataPullConfig:
        '''
        :stability: experimental
        '''
        result = self._values.get("pull_config")
        assert result is not None, "Required property 'pull_config' is missing"
        return typing.cast(DataPullConfig, result)

    @builtins.property
    def schedule(self) -> _aws_cdk_aws_events_ceddda9d.Schedule:
        '''
        :stability: experimental
        '''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(_aws_cdk_aws_events_ceddda9d.Schedule, result)

    @builtins.property
    def schedule_properties(self) -> typing.Optional[ScheduleProperties]:
        '''
        :stability: experimental
        '''
        result = self._values.get("schedule_properties")
        return typing.cast(typing.Optional[ScheduleProperties], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnScheduleFlowProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RedshiftConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.RedshiftConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        basic_auth: typing.Union[RedshiftConnectorBasicCredentials, typing.Dict[builtins.str, typing.Any]],
        cluster: _aws_cdk_aws_redshift_alpha_9727f5af.ICluster,
        database_name: builtins.str,
        intermediate_location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
        bucket_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        data_api_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param basic_auth: 
        :param cluster: (experimental) The Redshift cluster to use this connector profile with.
        :param database_name: (experimental) The name of the database which the RedshiftConnectorProfile will be working with.
        :param intermediate_location: (experimental) An intermediate location for the data retrieved from the flow source that will be further transferred to the Redshfit database.
        :param bucket_access_role: (experimental) An IAM Role that the Redshift cluster will assume to get data from the intermiediate S3 Bucket.
        :param data_api_role: (experimental) An IAM Role that AppFlow will assume to interact with the Redshift cluster's Data API. Default: autogenerated IAM role
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a58ef0e10db44b1b1bf9a8290423bc02cb64eed592a0f44d8f14f809ad3d0ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RedshiftConnectorProfileProps(
            basic_auth=basic_auth,
            cluster=cluster,
            database_name=database_name,
            intermediate_location=intermediate_location,
            bucket_access_role=bucket_access_role,
            data_api_role=data_api_role,
            key=key,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "RedshiftConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4dd394b83ad709efa3566a77735fda086d2c8dfc273aeeccb14a570800fa0e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("RedshiftConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "RedshiftConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2278df91381897b463bd0b4bfb4b8dbcaf0ee452cb603acb731230cfde5974cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("RedshiftConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(IDestination)
class RedshiftDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.RedshiftDestination",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: typing.Union[RedshiftDestinationObject, typing.Dict[builtins.str, typing.Any]],
        profile: RedshiftConnectorProfile,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param object: (experimental) A Redshift table object (optionally with the schema).
        :param profile: (experimental) An instance of the.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        props = RedshiftDestinationProps(
            object=object, profile=profile, error_handling=error_handling
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4b4b06cb0cb403843553ae93654f4667c11e8d1be7a5f6df39b0bc7265893d3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IDestination)
class S3Destination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.S3Destination",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
        catalog: typing.Optional[typing.Union[S3Catalog, typing.Dict[builtins.str, typing.Any]]] = None,
        formatting: typing.Optional[typing.Union[S3OutputFormatting, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param location: (experimental) The S3 location of the files with the retrieved data.
        :param catalog: (experimental) The AWS Glue cataloging options.
        :param formatting: (experimental) The formatting options for the output files.

        :stability: experimental
        '''
        props = S3DestinationProps(
            location=location, catalog=catalog, formatting=formatting
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5862768538371b3073f16756f588d1e5dda667285c69b64f9f36b872298e0ba)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(ISource)
class S3Source(metaclass=jsii.JSIIMeta, jsii_type="@cdklabs/cdk-appflow.S3Source"):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        prefix: builtins.str,
        format: typing.Optional[typing.Union[S3InputFormat, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param bucket: 
        :param prefix: 
        :param format: 

        :stability: experimental
        '''
        props = S3SourceProps(bucket=bucket, prefix=prefix, format=format)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1e09e5f5312a9f8751cf5ce9d37ff5134334869d46594888883266c8504ea46)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class SAPOdataConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SAPOdataConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        application_host_url: builtins.str,
        application_service_path: builtins.str,
        client_number: builtins.str,
        logon_language: builtins.str,
        basic_auth: typing.Optional[typing.Union[SAPOdataBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        o_auth: typing.Optional[typing.Union[SAPOdataOAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
        port_number: typing.Optional[jsii.Number] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param application_host_url: 
        :param application_service_path: 
        :param client_number: 
        :param logon_language: 
        :param basic_auth: 
        :param o_auth: 
        :param port_number: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1456a6c00e75acdfb46d10ac9e74fd8a326dbbb53336209c40da1bf1772dc678)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SAPOdataConnectorProfileProps(
            application_host_url=application_host_url,
            application_service_path=application_service_path,
            client_number=client_number,
            logon_language=logon_language,
            basic_auth=basic_auth,
            o_auth=o_auth,
            port_number=port_number,
            key=key,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "SAPOdataConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a6386649257a15b140d1f567e872eeeee4f4afe56bbb09734eb8b164e005830)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SAPOdataConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "SAPOdataConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65d328d60d5002bf9c8a09117a27e9b1e946b48879e17ad76aba5c6fd23857c8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SAPOdataConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(IDestination)
class SAPOdataDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SAPOdataDestination",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        operation: WriteOperation,
        profile: SAPOdataConnectorProfile,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        success_response_handling: typing.Optional[typing.Union[SAPOdataSuccessResponseHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param object: (experimental) The SAPOdata object for which the operation is to be set.
        :param operation: 
        :param profile: 
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the SAPOdata destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.
        :param success_response_handling: 

        :stability: experimental
        '''
        props = SAPOdataDestinationProps(
            object=object,
            operation=operation,
            profile=profile,
            error_handling=error_handling,
            success_response_handling=success_response_handling,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be9c75208a53ebc4db44ac27cc9aaac34a0b9ac8e574e73ff8a4a30fa1b7b46c)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(ISource)
class SAPOdataSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SAPOdataSource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        profile: SAPOdataConnectorProfile,
    ) -> None:
        '''
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = SAPOdataSourceProps(object=object, profile=profile)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0026fc92ed92f4c9cabaa7c920e2d283ecacf980920ee014d8bef28dfb74a01a)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class SalesforceConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SalesforceConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_url: builtins.str,
        o_auth: typing.Union[SalesforceOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        is_sandbox: typing.Optional[builtins.bool] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_url: 
        :param o_auth: 
        :param is_sandbox: Default: false
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__971cdd11384ff73d58d6d421eac3224b366d50d8ce1505049b566c9100872982)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SalesforceConnectorProfileProps(
            instance_url=instance_url,
            o_auth=o_auth,
            is_sandbox=is_sandbox,
            key=key,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "SalesforceConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e9cb36a47dea6920a365a064afad384a739bd0c19f1536826167577529e475d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SalesforceConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "SalesforceConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6143d77fe422945c9a8f9f82025a860f0b13de560638015c9163a5a9040ca095)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SalesforceConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        properties = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [properties]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        properties = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [properties]))


@jsii.implements(IDestination)
class SalesforceDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SalesforceDestination",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        operation: WriteOperation,
        profile: SalesforceConnectorProfile,
        data_transfer_api: typing.Optional[SalesforceDataTransferApi] = None,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param object: (experimental) The Salesforce object for which the operation is to be set.
        :param operation: 
        :param profile: 
        :param data_transfer_api: (experimental) Specifies which Salesforce API is used by Amazon AppFlow when your flow transfers data to Salesforce.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        props = SalesforceDestinationProps(
            object=object,
            operation=operation,
            profile=profile,
            data_transfer_api=data_transfer_api,
            error_handling=error_handling,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dee9194e1f6c5e09118515e69827c61c083ee45cb92df1fbfc9892e9d54ff75f)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class SalesforceMarketingCloudConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_url: builtins.str,
        o_auth: typing.Union[SalesforceMarketingCloudOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_url: 
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8410f844ea9b96fa7a6e2f3518a5fec1a35a25a685a6fd7e2aa919f6daf34a69)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SalesforceMarketingCloudConnectorProfileProps(
            instance_url=instance_url, o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "SalesforceMarketingCloudConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dfe81c83ad5453bac6f9afed24e1092edd26038b0f26f9a7715823dd6be9013)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SalesforceMarketingCloudConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "SalesforceMarketingCloudConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10e4e0603463cd481a8c7c66d1a2ae2e258c5f30a96ad40831f438aeb5714ab2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SalesforceMarketingCloudConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class SalesforceMarketingCloudSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SalesforceMarketingCloudSource",
):
    '''(experimental) A class that represents a Salesforce Marketing Cloud Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: SalesforceMarketingCloudConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = SalesforceMarketingCloudSourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56dbfc65e9095e0421b0e95f214dc50199e598e4172ae2acb02d9ded12082332)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(ISource)
class SalesforceSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SalesforceSource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        profile: SalesforceConnectorProfile,
        api_version: typing.Optional[builtins.str] = None,
        data_transfer_api: typing.Optional[SalesforceDataTransferApi] = None,
        enable_dynamic_field_update: typing.Optional[builtins.bool] = None,
        include_deleted_records: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 
        :param data_transfer_api: (experimental) Specifies which Salesforce API is used by Amazon AppFlow when your flow transfers data from Salesforce.
        :param enable_dynamic_field_update: 
        :param include_deleted_records: 

        :stability: experimental
        '''
        props = SalesforceSourceProps(
            object=object,
            profile=profile,
            api_version=api_version,
            data_transfer_api=data_transfer_api,
            enable_dynamic_field_update=enable_dynamic_field_update,
            include_deleted_records=include_deleted_records,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d75665b942bd54e4d796605d1783ec9b72c14a580d2a0908e9cb1017bb7043d6)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class ServiceNowConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ServiceNowConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        basic_auth: typing.Union[ServiceNowBasicSettings, typing.Dict[builtins.str, typing.Any]],
        instance_url: builtins.str,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param basic_auth: 
        :param instance_url: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b3879038be1a4e5f7230bc71ada45cc46a2e95edf8846a895bce14e71525254)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ServiceNowConnectorProfileProps(
            basic_auth=basic_auth, instance_url=instance_url, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "ServiceNowConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc536210ddd6cc47417ce5407ff85ce1a78d932f268015124e63190beb683f52)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("ServiceNowConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "ServiceNowConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d74eb3f8c13441d3702ed399f4902f3d927af2d3fb1f3a56058885640d44c856)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("ServiceNowConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class ServiceNowSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ServiceNowSource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        profile: ServiceNowConnectorProfile,
    ) -> None:
        '''
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = ServiceNowSourceProps(object=object, profile=profile)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e637407ea094bc9b64340ae13ad48f098c55d05718b6aec5a8e34f6b74c96748)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class SlackConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SlackConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_url: builtins.str,
        o_auth: typing.Union[SlackOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_url: 
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0128d0be60f75daae2247525587b1088f9493b303433c0e91bf36df088f1cdc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SlackConnectorProfileProps(
            instance_url=instance_url, o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "SlackConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6d7be495d76a6378875da67c6db9335aa8809f0d4212fa3571d8f36bcef7a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SlackConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "SlackConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d301278adbfbe76bb9432169d16b9329b86fc9f8c67b465a86f02c352e56c443)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SlackConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class SlackSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SlackSource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        profile: SlackConnectorProfile,
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        props = SlackSourceProps(
            object=object, profile=profile, api_version=api_version
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a922546c73247e33c6ba160429e170e96058ecb38cef1fcdf8eb5e60c72bbc66)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class SnowflakeConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SnowflakeConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: builtins.str,
        basic_auth: typing.Union[SnowflakeBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
        database: builtins.str,
        location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
        stage: builtins.str,
        warehouse: builtins.str,
        integration: typing.Optional[typing.Union[SnowflakeStorageIntegration, typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
        schema: typing.Optional[builtins.str] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param account: 
        :param basic_auth: 
        :param database: (experimental) The name of the Snowflake database.
        :param location: 
        :param stage: (experimental) The name of the Snowflake stage.
        :param warehouse: (experimental) The name of the Snowflake warehouse.
        :param integration: (experimental) Details of the Snowflake Storage Integration. When provided, this construct will automatically create an IAM Role allowing access to the S3 Bucket which will be available as a [integrationROle property]{@link SnowflakeConnectorProfile#integrationRole } For details of the integration see {@link https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration}
        :param region: 
        :param schema: (experimental) The name of the Snowflake schema. Default: PUBLIC
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dd1063a040290a9477ba77cf2296e4ada3d8751608122952462320895016dd5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SnowflakeConnectorProfileProps(
            account=account,
            basic_auth=basic_auth,
            database=database,
            location=location,
            stage=stage,
            warehouse=warehouse,
            integration=integration,
            region=region,
            schema=schema,
            key=key,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "SnowflakeConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e45fdc5fb210a90226ec328404153f805b74ea3af4d92b750e7a7b8a0a540eb5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("SnowflakeConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "SnowflakeConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e8b5f134e73c7420c208bd3ac5f610bc4e9b20cbac0e9ae51f3a8f40cd09921)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SnowflakeConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))

    @builtins.property
    @jsii.member(jsii_name="integrationRole")
    def integration_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The AWS IAM Role for the storage integration with Snowflake.

        Available only if [SnowflakeConnectorProfileProps's integration property]{@link SnowflakeConnectorProfileProps#integration } is provided.

        For more details see {@link https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration}

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "integrationRole"))


@jsii.implements(IDestination)
class SnowflakeDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.SnowflakeDestination",
):
    '''(experimental) A Snowflake destination.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: typing.Union[SnowflakeDestinationObject, typing.Dict[builtins.str, typing.Any]],
        profile: SnowflakeConnectorProfile,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param object: (experimental) A Snowflake table object (optionally with the schema).
        :param profile: (experimental) A Snowflake connector profile instance.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the Salesforce destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        props = SnowflakeDestinationProps(
            object=object, profile=profile, error_handling=error_handling
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97be675a19891adcd3ba67bd78ff2033e0c6f9cf115d622f3d48b237299426ea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IFlow)
class TriggeredFlowBase(
    FlowBase,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@cdklabs/cdk-appflow.TriggeredFlowBase",
):
    '''(experimental) A base class for triggered flows.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        type: FlowType,
        status: typing.Optional[FlowStatus] = None,
        trigger_config: typing.Optional[typing.Union[TriggerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        destination: IDestination,
        mappings: typing.Sequence[IMapping],
        source: ISource,
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence[IFilter]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param type: 
        :param status: 
        :param trigger_config: 
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13e29f4a8761d1eafa730da5c88359c07635eb7cd018ce40a9576c09b4f70b53)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = FlowBaseProps(
            type=type,
            status=status,
            trigger_config=trigger_config,
            destination=destination,
            mappings=mappings,
            source=source,
            description=description,
            filters=filters,
            key=key,
            name=name,
            transforms=transforms,
            validations=validations,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="setStatus")
    @builtins.classmethod
    def set_status(
        cls,
        auto_activate: typing.Optional[builtins.bool] = None,
        status: typing.Optional[FlowStatus] = None,
    ) -> typing.Optional[FlowStatus]:
        '''
        :param auto_activate: - a boolean value indicating whether to automatically activate the flow.
        :param status: - a {@link FlowStatus} value indicating the status to set on the flow.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2ad24e9750ce2b71d025e53bf1a90ab832d3b3158aa3c1d1b6854448d97223b)
            check_type(argname="argument auto_activate", value=auto_activate, expected_type=type_hints["auto_activate"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        return typing.cast(typing.Optional[FlowStatus], jsii.sinvoke(cls, "setStatus", [auto_activate, status]))

    @jsii.member(jsii_name="onDeactivated")
    @abc.abstractmethod
    def on_deactivated(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        ...


class _TriggeredFlowBaseProxy(
    TriggeredFlowBase,
    jsii.proxy_for(FlowBase), # type: ignore[misc]
):
    @jsii.member(jsii_name="onDeactivated")
    def on_deactivated(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95dacf4b74f5f17ded6d934b31d52c2f28e41c83bb0b5473ad280d31b95e888b)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onDeactivated", [id, options]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, TriggeredFlowBase).__jsii_proxy_class__ = lambda : _TriggeredFlowBaseProxy


class ZendeskConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ZendeskConnectorProfile",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_url: builtins.str,
        o_auth: typing.Union[ZendeskOAuthSettings, typing.Dict[builtins.str, typing.Any]],
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param instance_url: 
        :param o_auth: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d87ab1118f8aac7fd9553e0cec17f7aa9bdde8eb8268a14bb2dab10e12e5572b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ZendeskConnectorProfileProps(
            instance_url=instance_url, o_auth=o_auth, key=key, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "ZendeskConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a01eaa845aed42a839b2acc7400a2b64541982442ebece58ad0f08f47078a424)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("ZendeskConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "ZendeskConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cc9bb96eacc438143c77942ba4c355dc1966ea85ac7a73bdb610d472467138f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("ZendeskConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [props]))


@jsii.implements(ISource)
class ZendeskSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.ZendeskSource",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        profile: ZendeskConnectorProfile,
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        props = ZendeskSourceProps(
            object=object, profile=profile, api_version=api_version
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2097f06da6031382a5fcb7073e896e199a7e0bd4857a9865d1fcc4aaf0fc891d)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class AmazonRdsForPostgreSqlConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.AmazonRdsForPostgreSqlConnectorProfile",
):
    '''(experimental) The connector profile for the Amazon RDS for PostgreSQL connector.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        basic_auth: typing.Union[AmazonRdsForPostgreSqlBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
        database: builtins.str,
        hostname: builtins.str,
        port: typing.Optional[jsii.Number] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a new instance of the AmazonRdsForPostgreSqlConnectorProfile.

        :param scope: the Construct scope for this connector profile.
        :param id: the id of this connector profile.
        :param basic_auth: (experimental) The auth settings for the profile.
        :param database: (experimental) The name of the PostgreSQL database.
        :param hostname: (experimental) The PostgreSQL hostname.
        :param port: (experimental) The PostgreSQL communication port.
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__598bab69fc3c82125f6db3d072992382b187be9b68dd22b799f9391166cf138c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AmazonRdsForPostgreSqlConnectorProfileProps(
            basic_auth=basic_auth,
            database=database,
            hostname=hostname,
            port=port,
            key=key,
            name=name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "AmazonRdsForPostgreSqlConnectorProfile":
        '''(experimental) Imports an existing AmazonRdsForPostgreSqlConnectorProfile.

        :param scope: the scope for the connector profile.
        :param id: the connector profile's ID.
        :param arn: the ARN for the existing connector profile.

        :return: An instance of the AmazonRdsForPostreSqlConnectorProfile

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1068ccf524cfa09953853645fd0d3ad1292f24c43170d6785a588eaa0bc8cc76)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("AmazonRdsForPostgreSqlConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "AmazonRdsForPostgreSqlConnectorProfile":
        '''(experimental) Imports an existing AmazonRdsForPostgreSqlConnectorProfile.

        :param scope: the scope for the connector profile.
        :param id: the connector profile's ID.
        :param name: the name for the existing connector profile.

        :return: An instance of the AmazonRdsForPostreSqlConnectorProfile

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1927661bcb638d1a9f5a24011091984bce47f46d3ab478605a61a7bc7ebcdf8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("AmazonRdsForPostgreSqlConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        _props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [_props]))


@jsii.implements(IDestination)
class AmazonRdsForPostgreSqlDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.AmazonRdsForPostgreSqlDestination",
):
    '''(experimental) Represents a destination for the Amazon RDS for PostgreSQL connector.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: typing.Union[AmazonRdsForPostgreSqlObject, typing.Dict[builtins.str, typing.Any]],
        profile: AmazonRdsForPostgreSqlConnectorProfile,
        api_version: typing.Optional[builtins.str] = None,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Creates a new instance of the AmazonRdsForPostgreSqlDestination.

        :param object: (experimental) The destination object table to write to.
        :param profile: (experimental) The profile to use with the destination.
        :param api_version: (experimental) The Amazon AppFlow Api Version.
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        props = AmazonRdsForPostgreSqlDestinationProps(
            object=object,
            profile=profile,
            api_version=api_version,
            error_handling=error_handling,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5d92b91aa48252ae6085ca88803bb9621caf7e8f0b9a83834348de26d8f497c)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


class AsanaConnectorProfile(
    ConnectorProfileBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.AsanaConnectorProfile",
):
    '''(experimental) A class that represents a Asana Connector Profile.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        pat_token: _aws_cdk_ceddda9d.SecretValue,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param pat_token: 
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a58bdbd0832b8777a6069753afb1fb46c89bf3b05a095268a3c14431bd1adde)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AsanaConnectorProfileProps(pat_token=pat_token, key=key, name=name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromConnectionProfileArn")
    @builtins.classmethod
    def from_connection_profile_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        arn: builtins.str,
    ) -> "AsanaConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cfdc6017db78a12701ec0c2cc86ea3ba126285b5ac69bb179086503f6b06191)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
        return typing.cast("AsanaConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileArn", [scope, id, arn]))

    @jsii.member(jsii_name="fromConnectionProfileName")
    @builtins.classmethod
    def from_connection_profile_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        name: builtins.str,
    ) -> "AsanaConnectorProfile":
        '''
        :param scope: -
        :param id: -
        :param name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bff0c5e2bcd9170090e9693991889256002bf6328945d0f4773bf532282213fd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("AsanaConnectorProfile", jsii.sinvoke(cls, "fromConnectionProfileName", [scope, id, name]))

    @jsii.member(jsii_name="buildConnectorProfileCredentials")
    def _build_connector_profile_credentials(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfileCredentialsProperty, jsii.invoke(self, "buildConnectorProfileCredentials", [props]))

    @jsii.member(jsii_name="buildConnectorProfileProperties")
    def _build_connector_profile_properties(
        self,
        *,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty:
        '''
        :param key: (experimental) TODO: think if this should be here as not all connector profiles have that.
        :param name: 

        :stability: experimental
        '''
        _props = ConnectorProfileProps(key=key, name=name)

        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnConnectorProfile.ConnectorProfilePropertiesProperty, jsii.invoke(self, "buildConnectorProfileProperties", [_props]))


@jsii.implements(ISource)
class AsanaSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.AsanaSource",
):
    '''(experimental) A class that represents a Asana v3 Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        object: builtins.str,
        profile: AsanaConnectorProfile,
        api_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param object: 
        :param profile: 
        :param api_version: 

        :stability: experimental
        '''
        props = AsanaSourceProps(
            object=object, profile=profile, api_version=api_version
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bde8e7c5e26495b30b4764f5ede134b7ed0c22527dd3faff8410c0120a1a93b4)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IDestination)
class EventBridgeDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.EventBridgeDestination",
):
    '''(experimental) This class represents AppFlow's EventBridge destination.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        partner_bus: builtins.str,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param partner_bus: 
        :param error_handling: 

        :stability: experimental
        '''
        props = EventBridgeDestinationProps(
            partner_bus=partner_bus, error_handling=error_handling
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f2f47cdd9c92993f8180f795883ea922561afaaf0dd29d1fcc7149fc980816b)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IFilter)
class Filter(
    OperationBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.Filter",
):
    '''(experimental) A representation of a mapping operation, that is an operation filtering records at the source.

    :stability: experimental
    '''

    def __init__(self, condition: FilterCondition) -> None:
        '''
        :param condition: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1838c353b79166cff9f0c099c3a545db7b0fc4a6bdf92a753c8c0555355f1d7)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        jsii.create(self.__class__, self, [condition])

    @jsii.member(jsii_name="when")
    @builtins.classmethod
    def when(cls, condition: FilterCondition) -> "Filter":
        '''(experimental) Builds a filter operation on source.

        :param condition: a.

        :see: FilterCondition instance
        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dc11e36c8e97ec161cf0e41e354e44678d3c7f9493a45862d7e905722153c42)
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
        return typing.cast("Filter", jsii.sinvoke(cls, "when", [condition]))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> FilterCondition:
        '''
        :stability: experimental
        '''
        return typing.cast(FilterCondition, jsii.get(self, "condition"))


@jsii.implements(ISource)
class GitHubSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GitHubSource",
):
    '''(experimental) A class that represents a Google Analytics v4 Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: GitHubConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = GitHubSourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f7df3fd64b76749dce46b072eb594c695bd5beebbe16ce8da249163dadc67e2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(ISource)
class GoogleAdsSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GoogleAdsSource",
):
    '''(experimental) A class that represents a Google Ads v4 Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: GoogleAdsConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = GoogleAdsSourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff3d2380df317e993005c128fbb6bbacadcada6d54f259f89a3387f9d3f739e6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(ISource)
class GoogleAnalytics4Source(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GoogleAnalytics4Source",
):
    '''(experimental) A class that represents a Google Analytics v4 Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: builtins.str,
        profile: GoogleAnalytics4ConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = GoogleAnalytics4SourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cd876dce9ba6511ecfc8571441244f3a14d9352d9abfe9a597cf724a29014b1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(ISource)
class GoogleBigQuerySource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.GoogleBigQuerySource",
):
    '''(experimental) A class that represents a Google BigQuery Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: builtins.str,
        object: typing.Union[GoogleBigQueryObject, typing.Dict[builtins.str, typing.Any]],
        profile: GoogleBigQueryConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param object: 
        :param profile: 

        :stability: experimental
        '''
        props = GoogleBigQuerySourceProps(
            api_version=api_version, object=object, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d5edd63aaccd54eeb9f7c31e4ec6387af3a10d4f0415ee5a2af8d6f3346b564)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IDestination)
class HubSpotDestination(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.HubSpotDestination",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: HubSpotApiVersion,
        entity: typing.Sequence[builtins.str],
        operation: WriteOperation,
        profile: HubSpotConnectorProfile,
        error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param api_version: 
        :param entity: 
        :param operation: 
        :param profile: 
        :param error_handling: (experimental) The settings that determine how Amazon AppFlow handles an error when placing data in the HubSpot destination. For example, this setting would determine if the flow should fail after one insertion error, or continue and attempt to insert every record regardless of the initial failure.

        :stability: experimental
        '''
        props = HubSpotDestinationProps(
            api_version=api_version,
            entity=entity,
            operation=operation,
            profile=profile,
            error_handling=error_handling,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        flow: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty:
        '''
        :param flow: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3076a4259c391aa8bfde0da045072f7e3d60236ba8ab4932330853b7819380bf)
            check_type(argname="argument flow", value=flow, expected_type=type_hints["flow"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.DestinationFlowConfigProperty, jsii.invoke(self, "bind", [flow]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(ISource)
class HubSpotSource(
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.HubSpotSource",
):
    '''(experimental) A class that represents a Hubspot Source.

    :stability: experimental
    '''

    def __init__(
        self,
        *,
        api_version: HubSpotApiVersion,
        entity: typing.Sequence[builtins.str],
        profile: HubSpotConnectorProfile,
    ) -> None:
        '''
        :param api_version: 
        :param entity: 
        :param profile: 

        :stability: experimental
        '''
        props = HubSpotSourceProps(
            api_version=api_version, entity=entity, profile=profile
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        scope: IFlow,
    ) -> _aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty:
        '''
        :param scope: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac553b95617d60e3e759e601d3adb0a1316d00975c3171e9d0d0cc95d2ed9f34)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        return typing.cast(_aws_cdk_aws_appflow_ceddda9d.CfnFlow.SourceFlowConfigProperty, jsii.invoke(self, "bind", [scope]))

    @builtins.property
    @jsii.member(jsii_name="connectorType")
    def connector_type(self) -> ConnectorType:
        '''(experimental) The AppFlow type of the connector that this source is implemented for.

        :stability: experimental
        '''
        return typing.cast(ConnectorType, jsii.get(self, "connectorType"))


@jsii.implements(IFlow)
class OnEventFlow(
    TriggeredFlowBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.OnEventFlow",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        auto_activate: typing.Optional[builtins.bool] = None,
        status: typing.Optional[FlowStatus] = None,
        destination: IDestination,
        mappings: typing.Sequence[IMapping],
        source: ISource,
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence[IFilter]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param auto_activate: 
        :param status: (experimental) The status to set on the flow. Use this over {@link autoActivate}.
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87a164f0be4a5d75d7089b4df6855c5ff83e9019490cd7856fab5d7232ac6f52)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OnEventFlowProps(
            auto_activate=auto_activate,
            status=status,
            destination=destination,
            mappings=mappings,
            source=source,
            description=description,
            filters=filters,
            key=key,
            name=name,
            transforms=transforms,
            validations=validations,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="onDeactivated")
    def on_deactivated(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b205dc908b59be5756e8804a9db3a2e274c5f0bed7a9f1686c9874eabfe4b34f)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onDeactivated", [id, options]))

    @jsii.member(jsii_name="onStatus")
    def on_status(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e905b80fb14b8a853fdbaf13a24111c841b000e327e3dd51c5655dbf8bdc8ff4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onStatus", [id, options]))


@jsii.implements(IFlow)
class OnScheduleFlow(
    TriggeredFlowBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-appflow.OnScheduleFlow",
):
    '''
    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        pull_config: typing.Union[DataPullConfig, typing.Dict[builtins.str, typing.Any]],
        schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
        schedule_properties: typing.Optional[typing.Union[ScheduleProperties, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_activate: typing.Optional[builtins.bool] = None,
        status: typing.Optional[FlowStatus] = None,
        destination: IDestination,
        mappings: typing.Sequence[IMapping],
        source: ISource,
        description: typing.Optional[builtins.str] = None,
        filters: typing.Optional[typing.Sequence[IFilter]] = None,
        key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        name: typing.Optional[builtins.str] = None,
        transforms: typing.Optional[typing.Sequence[ITransform]] = None,
        validations: typing.Optional[typing.Sequence[IValidation]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param pull_config: 
        :param schedule: 
        :param schedule_properties: 
        :param auto_activate: 
        :param status: (experimental) The status to set on the flow. Use this over {@link autoActivate}.
        :param destination: 
        :param mappings: 
        :param source: 
        :param description: 
        :param filters: 
        :param key: 
        :param name: 
        :param transforms: 
        :param validations: 

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14c889972d22be3a8c6b6f8373772766c112b75ebbd835bd5653c7494e51d7df)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = OnScheduleFlowProps(
            pull_config=pull_config,
            schedule=schedule,
            schedule_properties=schedule_properties,
            auto_activate=auto_activate,
            status=status,
            destination=destination,
            mappings=mappings,
            source=source,
            description=description,
            filters=filters,
            key=key,
            name=name,
            transforms=transforms,
            validations=validations,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="onDeactivated")
    def on_deactivated(
        self,
        id: builtins.str,
        *,
        target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
        cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
        rule_name: typing.Optional[builtins.str] = None,
    ) -> _aws_cdk_aws_events_ceddda9d.Rule:
        '''
        :param id: -
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.
        :param cross_stack_scope: The scope to use if the source of the rule and its target are in different Stacks (but in the same account & region). This helps dealing with cycles that often arise in these situations. Default: - none (the main scope will be used, even for cross-stack Events)
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3ad6452763aac3ac2da51fd43dd4b8dc75fe17b124c46e8b1456763d41cf6ba)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        options = _aws_cdk_aws_events_ceddda9d.OnEventOptions(
            target=target,
            cross_stack_scope=cross_stack_scope,
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
        )

        return typing.cast(_aws_cdk_aws_events_ceddda9d.Rule, jsii.invoke(self, "onDeactivated", [id, options]))


__all__ = [
    "AmazonRdsForPostgreSqlBasicAuthSettings",
    "AmazonRdsForPostgreSqlConnectorProfile",
    "AmazonRdsForPostgreSqlConnectorProfileProps",
    "AmazonRdsForPostgreSqlDestination",
    "AmazonRdsForPostgreSqlDestinationProps",
    "AmazonRdsForPostgreSqlObject",
    "AsanaConnectorProfile",
    "AsanaConnectorProfileProps",
    "AsanaSource",
    "AsanaSourceProps",
    "ConnectionMode",
    "ConnectorAuthenticationType",
    "ConnectorProfileBase",
    "ConnectorProfileProps",
    "ConnectorType",
    "DataPullConfig",
    "DataPullMode",
    "ErrorHandlingConfiguration",
    "EventBridgeDestination",
    "EventBridgeDestinationProps",
    "EventSources",
    "Field",
    "Filter",
    "FilterCondition",
    "FlowBase",
    "FlowBaseProps",
    "FlowProps",
    "FlowStatus",
    "FlowType",
    "GitHubApiVersion",
    "GitHubBasicAuthSettings",
    "GitHubConnectorProfile",
    "GitHubConnectorProfileProps",
    "GitHubOAuthEndpoints",
    "GitHubOAuthFlow",
    "GitHubOAuthSettings",
    "GitHubRefreshTokenGrantFlow",
    "GitHubSource",
    "GitHubSourceProps",
    "GoogleAdsApiVersion",
    "GoogleAdsConnectorProfile",
    "GoogleAdsConnectorProfileProps",
    "GoogleAdsOAuthEndpoints",
    "GoogleAdsOAuthFlow",
    "GoogleAdsOAuthSettings",
    "GoogleAdsRefreshTokenGrantFlow",
    "GoogleAdsSource",
    "GoogleAdsSourceProps",
    "GoogleAnalytics4ApiVersion",
    "GoogleAnalytics4ConnectorProfile",
    "GoogleAnalytics4ConnectorProfileProps",
    "GoogleAnalytics4OAuthEndpoints",
    "GoogleAnalytics4OAuthFlow",
    "GoogleAnalytics4OAuthSettings",
    "GoogleAnalytics4RefreshTokenGrantFlow",
    "GoogleAnalytics4Source",
    "GoogleAnalytics4SourceProps",
    "GoogleBigQueryApiVersion",
    "GoogleBigQueryConnectorProfile",
    "GoogleBigQueryConnectorProfileProps",
    "GoogleBigQueryOAuthEndpoints",
    "GoogleBigQueryOAuthFlow",
    "GoogleBigQueryOAuthSettings",
    "GoogleBigQueryObject",
    "GoogleBigQueryRefreshTokenGrantFlow",
    "GoogleBigQuerySource",
    "GoogleBigQuerySourceProps",
    "HubSpotApiVersion",
    "HubSpotConnectorProfile",
    "HubSpotConnectorProfileProps",
    "HubSpotDestination",
    "HubSpotDestinationProps",
    "HubSpotOAuthEndpoints",
    "HubSpotOAuthFlow",
    "HubSpotOAuthSettings",
    "HubSpotRefreshTokenGrantFlow",
    "HubSpotSource",
    "HubSpotSourceProps",
    "IConnectorProfile",
    "IDestination",
    "IFilter",
    "IFlow",
    "IMapping",
    "IOperation",
    "ISource",
    "ITask",
    "ITransform",
    "IValidation",
    "IVertex",
    "JdbcDriver",
    "JdbcSmallDataScaleBasicAuthSettings",
    "JdbcSmallDataScaleConnectorProfile",
    "JdbcSmallDataScaleConnectorProfileProps",
    "JdbcSmallDataScaleObject",
    "JdbcSmallDataScaleSource",
    "JdbcSmallDataScaleSourceProps",
    "MailchimpApiVersion",
    "MailchimpConnectorProfile",
    "MailchimpConnectorProfileProps",
    "MailchimpSource",
    "MailchimpSourceProps",
    "MapAllConfig",
    "Mapping",
    "MarketoConnectorProfile",
    "MarketoConnectorProfileProps",
    "MarketoInstanceUrlBuilder",
    "MarketoOAuthClientCredentialsFlow",
    "MarketoOAuthFlow",
    "MarketoOAuthSettings",
    "MarketoSource",
    "MarketoSourceProps",
    "MicrosoftDynamics365ApiUrlBuilder",
    "MicrosoftDynamics365ApiVersion",
    "MicrosoftDynamics365ConnectorProfile",
    "MicrosoftDynamics365ConnectorProfileProps",
    "MicrosoftDynamics365OAuthEndpointsSettings",
    "MicrosoftDynamics365OAuthFlow",
    "MicrosoftDynamics365OAuthSettings",
    "MicrosoftDynamics365RefreshTokenGrantFlow",
    "MicrosoftDynamics365Source",
    "MicrosoftDynamics365SourceProps",
    "MicrosoftDynamics365TokenUrlBuilder",
    "MicrosoftSharepointOnlineApiVersion",
    "MicrosoftSharepointOnlineConnectorProfile",
    "MicrosoftSharepointOnlineConnectorProfileProps",
    "MicrosoftSharepointOnlineOAuthEndpointsSettings",
    "MicrosoftSharepointOnlineOAuthFlow",
    "MicrosoftSharepointOnlineOAuthSettings",
    "MicrosoftSharepointOnlineObject",
    "MicrosoftSharepointOnlineRefreshTokenGrantFlow",
    "MicrosoftSharepointOnlineSource",
    "MicrosoftSharepointOnlineSourceProps",
    "MicrosoftSharepointOnlineTokenUrlBuilder",
    "OAuth2GrantType",
    "OnDemandFlow",
    "OnDemandFlowProps",
    "OnEventFlow",
    "OnEventFlowProps",
    "OnScheduleFlow",
    "OnScheduleFlowProps",
    "OperationBase",
    "RedshiftConnectorBasicCredentials",
    "RedshiftConnectorProfile",
    "RedshiftConnectorProfileProps",
    "RedshiftDestination",
    "RedshiftDestinationObject",
    "RedshiftDestinationProps",
    "S3Catalog",
    "S3Destination",
    "S3DestinationProps",
    "S3FileAggregation",
    "S3InputFileType",
    "S3InputFormat",
    "S3Location",
    "S3OutputAggregationType",
    "S3OutputFilePrefix",
    "S3OutputFilePrefixFormat",
    "S3OutputFilePrefixHierarchy",
    "S3OutputFilePrefixType",
    "S3OutputFileType",
    "S3OutputFormatting",
    "S3Source",
    "S3SourceProps",
    "SAPOdataBasicAuthSettings",
    "SAPOdataConnectorProfile",
    "SAPOdataConnectorProfileProps",
    "SAPOdataDestination",
    "SAPOdataDestinationProps",
    "SAPOdataOAuthEndpoints",
    "SAPOdataOAuthFlows",
    "SAPOdataOAuthRefreshTokenGrantFlow",
    "SAPOdataOAuthSettings",
    "SAPOdataSource",
    "SAPOdataSourceProps",
    "SAPOdataSuccessResponseHandlingConfiguration",
    "SalesforceConnectorProfile",
    "SalesforceConnectorProfileProps",
    "SalesforceDataTransferApi",
    "SalesforceDestination",
    "SalesforceDestinationProps",
    "SalesforceMarketingCloudApiVersions",
    "SalesforceMarketingCloudConnectorProfile",
    "SalesforceMarketingCloudConnectorProfileProps",
    "SalesforceMarketingCloudFlowSettings",
    "SalesforceMarketingCloudOAuthClientSettings",
    "SalesforceMarketingCloudOAuthEndpoints",
    "SalesforceMarketingCloudOAuthSettings",
    "SalesforceMarketingCloudSource",
    "SalesforceMarketingCloudSourceProps",
    "SalesforceOAuthFlow",
    "SalesforceOAuthRefreshTokenGrantFlow",
    "SalesforceOAuthSettings",
    "SalesforceSource",
    "SalesforceSourceProps",
    "ScheduleProperties",
    "ServiceNowBasicSettings",
    "ServiceNowConnectorProfile",
    "ServiceNowConnectorProfileProps",
    "ServiceNowInstanceUrlBuilder",
    "ServiceNowSource",
    "ServiceNowSourceProps",
    "SlackConnectorProfile",
    "SlackConnectorProfileProps",
    "SlackInstanceUrlBuilder",
    "SlackOAuthSettings",
    "SlackSource",
    "SlackSourceProps",
    "SnowflakeBasicAuthSettings",
    "SnowflakeConnectorProfile",
    "SnowflakeConnectorProfileProps",
    "SnowflakeDestination",
    "SnowflakeDestinationObject",
    "SnowflakeDestinationProps",
    "SnowflakeStorageIntegration",
    "Task",
    "TaskConnectorOperator",
    "TaskProperty",
    "Transform",
    "TriggerConfig",
    "TriggerProperties",
    "TriggeredFlowBase",
    "TriggeredFlowBaseProps",
    "Validation",
    "ValidationAction",
    "ValidationCondition",
    "WriteOperation",
    "WriteOperationType",
    "ZendeskConnectorProfile",
    "ZendeskConnectorProfileProps",
    "ZendeskInstanceUrlBuilder",
    "ZendeskOAuthSettings",
    "ZendeskSource",
    "ZendeskSourceProps",
]

publication.publish()

def _typecheckingstub__96e3255e9267c9a22750bc9922aeb173dcb6bc4bb8b2ffc75d4eb899f747d161(
    *,
    password: _aws_cdk_ceddda9d.SecretValue,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f725757438cce70c8bc12ec03c1a8c12b32e2a6f3fe7ec3769638361956d149b(
    *,
    object: typing.Union[AmazonRdsForPostgreSqlObject, typing.Dict[builtins.str, typing.Any]],
    profile: AmazonRdsForPostgreSqlConnectorProfile,
    api_version: typing.Optional[builtins.str] = None,
    error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c725a2a36b9f4a2b583c74c11e02a973fee96febd089ef6e106e6e173726e21(
    *,
    schema: builtins.str,
    table: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a10110e387fc84d27f617a32384b0edaf667147be8413bf5dccb7aa2c9a600a(
    *,
    object: builtins.str,
    profile: AsanaConnectorProfile,
    api_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d2b41de7a95f2c15f3a2e708fae5b91cad064354f541d048f25529a389dc9a8(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dedf196b2eb8984e508697aeef563f4abe76df9549bc1abbd76ea89b5090ced3(
    name: builtins.str,
    is_custom: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9a219093b3770ee1eb01f8ea621bdc4d6af591bcd53b51d77b6cd192fe4df56(
    *,
    mode: DataPullMode,
    timestamp_field: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b902b20c49881b25e7253d2906d885c0512a58520c7a25f90d4e3da6113fc57c(
    *,
    error_location: typing.Optional[typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]]] = None,
    fail_on_first_error: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ee9438969865bad2afd0571f058aa9ce19717393528c2a3f61f5b7b1f1e29c1(
    *,
    partner_bus: builtins.str,
    error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05a2218bf349477bb87b155c2ac98cf73f23b1d586a50056874c4baf9ed0d409(
    suffix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c577310c8c6e1b3811a8040d35a1af0afda03b22fc2c2924cdb61a990adfb5c6(
    *,
    name: builtins.str,
    data_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16baec51c19521c7c18d8fe59a8371588c6a927e50a836c930d9ebf33876dda6(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    filter: builtins.str,
    properties: typing.Sequence[typing.Union[TaskProperty, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a875f6b5f7bf87a4f177870de2e0fafb24e434a660936970e77fc3d0c659d5f3(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[builtins.bool, typing.Sequence[builtins.bool]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa94007128b06e5433d43cbaaf5c9378035abd60112ffe8d58c870c9b8e299b6(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[builtins.bool, typing.Sequence[builtins.bool]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ac4b1ff70f65e3e1219f41182dc75ee9e7ef453ba07b91b395813f9cbec231(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[jsii.Number, typing.Sequence[jsii.Number]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__290508e525c94bd401dcfe60655c0c6d59a50149a374f408ba135bf3b4ff64b5(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4afeedbae2168afc195222b93567587fa83ec21e60fbf57686855c6fe38f493e(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ca157f12d69a9aaf9ecb1bd1106e099d1e02e7fb48142c43d5e59a94da2b122(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31008f1be0a65f5601c54b82706f09a63fde99745a72ff0146f4c3a0a5e1f15d(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c33472102821a812d20b857c2f029eebed54a9c9feab807739a4ace1ad3957c3(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[jsii.Number, typing.Sequence[jsii.Number]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1e674adc3eb5dea2e21b7980e89b87e7cd32b22ab3dafc8f2516cc2d576acce(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[builtins.str, typing.Sequence[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e84b1e1d02ac2c57996ef297a0120f2460eb95456333571b6516b3ae2c568a72(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[builtins.str, typing.Sequence[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb2d9d82e577a11bb47b45cc1005652cb6590a0fcfc6fe5e0aff16460086f5f3(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[builtins.str, typing.Sequence[builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6596d56f873254bdbea91a961316b1e426193af89f30b1d81b619372eeaba594(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    lower: datetime.datetime,
    upper: datetime.datetime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd22a2d553e04e7657f1cf1a5e834335d624cb0dddf2fae9d4f8cf34efbf41a4(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51b57011b2256e9228bd257aa6cd547ab315844abe8729773fefaa85e62dbb3e(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fe6c0395d580587e6d9c96e598196454ceb9a1817e3b6265dd3b775a6fce72d(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8afdbe101b79fa52a1e42a99869170a0c6b15655d14267d75bc25bd8a03b69c6(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c17beb7ddb040f7920e6fc36db02c529105115c35fac145e62bb6584c13d00c(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9499e24c9ac13e1d29a6a235699b246a24118d09cc7e401e1ad201e82f4734c2(
    field: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    val: typing.Union[datetime.datetime, typing.Sequence[datetime.datetime]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63e0314fa809fbb27cb2cb0dde8fe14293f94bc3d6910858bdd4063c08568061(
    *,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e268fe526bd12af421247f3a5e384e1b9df12194d12e6d23107fed19bd5c45d5(
    *,
    personal_access_token: _aws_cdk_ceddda9d.SecretValue,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61bc30b75d8ced92cd18e268f5591ba2f236cfdd046af8185ebe39c6855e419d(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    basic_auth: typing.Optional[typing.Union[GitHubBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    o_auth: typing.Optional[typing.Union[GitHubOAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ba14b32a0e8e2d79bdd5878a23ddee7374ed93c567a68e6b4ee82b692d52458(
    *,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31caa73fa95f06c2d89229e70b0c6cf337104851cd7e90d10041810b5c00623(
    *,
    refresh_token_grant: typing.Union[GitHubRefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab80f2151f523ffcee8042372b826ee33d7f4ba5aefc8b2bbb09f2ac154eb4f0(
    *,
    access_token: _aws_cdk_ceddda9d.SecretValue,
    endpoints: typing.Optional[typing.Union[GitHubOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d48e31e276996840860d7f9db140adf67c361f51fa5d3cacf8b5e94e1f332074(
    *,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9254d787e0613946edeb3abac41d0e02b840f68b1b72eb07a1e019c201ee8fa3(
    *,
    api_version: builtins.str,
    object: builtins.str,
    profile: GitHubConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d68581f43587a9b8d6c670235a257a8aac675685d0cb70a93e18a159c31d1fa(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    api_version: builtins.str,
    developer_token: _aws_cdk_ceddda9d.SecretValue,
    o_auth: typing.Union[GoogleAdsOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    manager_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b866abeabb5b404df587566da5ca60fc80ed7309f2ed1dc61e3f33fda4058aa(
    *,
    authorization: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d30be5ccf5bd5361e1685a3876eb56ea080887d90a0ba458775383c32bdb5071(
    *,
    refresh_token_grant: typing.Union[GoogleAdsRefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae01841af763bdb713516e7577ae0fd5949d5c91f72b7bc25c5630b03049456(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    endpoints: typing.Optional[typing.Union[GoogleAdsOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    flow: typing.Optional[typing.Union[GoogleAdsOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b4e3831023822364458e04692fe7434b8e23e7e6b259c8c24606bec1ffaaae(
    *,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96d3c97ac705591fcb0ee8e54809772b14e34c3ff09101140a14f17f16ced25f(
    *,
    api_version: builtins.str,
    object: builtins.str,
    profile: GoogleAdsConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9419ec87b9bd134e1c70777a9c8da70e653d9e3084a51d4a663a2983ee6b37e(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    o_auth: typing.Union[GoogleAnalytics4OAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f20189cf55481a97cb670d9b726f9d5a6fba015c9a9cc896b7e7e6ef2155596c(
    *,
    authorization: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d54d73d6d3c4814064b63102986f2535facdab1881fee4dc004e8e000da17f0(
    *,
    refresh_token_grant: typing.Union[GoogleAnalytics4RefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06303ef850b9e990f6fbb8ec4f2680f84193f23b51ccd77d204866d334de5556(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    endpoints: typing.Optional[typing.Union[GoogleAnalytics4OAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    flow: typing.Optional[typing.Union[GoogleAnalytics4OAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b8e5ad0344be660e939d8a9049f9e13319ccda543597d267f4807f2faf5b06(
    *,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c45b3cba2dab0afc04a8bb5504b43b124885419b0f8887d13343dfacf973ce7b(
    *,
    api_version: builtins.str,
    object: builtins.str,
    profile: GoogleAnalytics4ConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9973981517794de47b47c46a3990f4a143a2d783edad508f2569fd9a5b0b098(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    o_auth: typing.Union[GoogleBigQueryOAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd41b074442abbb69d9223775ef74cb136d886ea3f758594faff0f12201e9a62(
    *,
    authorization: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0ab06480e05444b0c04d4f3ef31da672c87ce88f0f25514058ba7f53135a6ad(
    *,
    refresh_token_grant: typing.Union[GoogleBigQueryRefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cf03c9dd60833d3c00e6be90fc05f6703613db62a4f929a452a11e32ae0aaef(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    endpoints: typing.Optional[typing.Union[GoogleBigQueryOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    flow: typing.Optional[typing.Union[GoogleBigQueryOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57d63574920e91b25ab7e6df19971d28d83212f260491db85c1e77043b0ae960(
    *,
    dataset: builtins.str,
    project: builtins.str,
    table: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d458fb271e77d6da1d2f7a891d0b7218ff53a799bd4a2b42faf3639ca6026884(
    *,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c40b8b595c94a8303138555bda9ad1b6d0ca076bb454205adc14900d796a4f6(
    *,
    api_version: builtins.str,
    object: typing.Union[GoogleBigQueryObject, typing.Dict[builtins.str, typing.Any]],
    profile: GoogleBigQueryConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2b51399bcb1bd54cdcdd3807c32527ae282f22f4bebe80fa302e196f0c5d962(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    o_auth: typing.Union[HubSpotOAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e671cee81f81b7b10893de67ae0fbff6fcce91ee33cd8b966a708e5a963434e(
    *,
    api_version: HubSpotApiVersion,
    entity: typing.Sequence[builtins.str],
    operation: WriteOperation,
    profile: HubSpotConnectorProfile,
    error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04cf8bba21518e1c7a3dbacf9d1b594b4eebe6a28dc327c78f6c51e31d96c1dc(
    *,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5251656d671e38b2bb0a04996caf851695251d1aebee10fc76744e6d74cda30f(
    *,
    refresh_token_grant: typing.Union[HubSpotRefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8731360eb4aae4d089d40080325bf59c21afd86e27a7daf8e5b25402ba927f(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    endpoints: typing.Optional[typing.Union[HubSpotOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    flow: typing.Optional[typing.Union[HubSpotOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b942055ffb6eb0b2f2b86333bb1c5fba057ff8ceecb37111500f6f8bb50edda9(
    *,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a560d5de39bbeb6a291b1135b0a32fdc42fbac6b2ed38ed29582e611f8c0d1(
    *,
    api_version: HubSpotApiVersion,
    entity: typing.Sequence[builtins.str],
    profile: HubSpotConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5552b7c97b017064cac75bd8f5d204e42ae9b7d420e7354699555396ba508e0(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08eabe4de6637500e424a8cdc75ccfceca6fbf225a1b42b189ff54b7c6ead630(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61c118209611ea60b7b0e5493b5cda2a16a36ee38e5f176b7e941ce7afe08468(
    flow: IFlow,
    source: ISource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b48af4a3da83426a2d0417ec6a9087adfdb2f12303453f044e67f619b1a8a52(
    flow: IFlow,
    source: ISource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb0c6a784d526fe673880a8dc8853f501be865bacf284293ad9648077787b15f(
    *,
    password: _aws_cdk_ceddda9d.SecretValue,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc14393bb8b8efbaa54178e594c59963d49e2b229727f448ac8fb291bbeb4995(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    basic_auth: typing.Union[JdbcSmallDataScaleBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
    database: builtins.str,
    driver: JdbcDriver,
    hostname: builtins.str,
    port: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e934abcd418f8a3346c0203b271d64a00de231c61d22b48d24e0c25a67b404e1(
    *,
    schema: builtins.str,
    table: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58c61c2bd9e826806d9e1a1c701fc3b78eb7b197b458672bd695b12d578c5093(
    *,
    object: typing.Union[JdbcSmallDataScaleObject, typing.Dict[builtins.str, typing.Any]],
    profile: JdbcSmallDataScaleConnectorProfile,
    api_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01619582f0540dc2247df97a632e56a45484d0e100a27d38e67e6ee1bf631032(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    api_key: _aws_cdk_ceddda9d.SecretValue,
    instance_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__997ea399b9fcc0497f84b977ed8f1cea34402f74de270398f7fab9b7ae8e7cf6(
    *,
    api_version: builtins.str,
    object: builtins.str,
    profile: MailchimpConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82007c94804b84589edff57bc8718212e6520637e6aa1a5e7f2cf7d6c731140a(
    *,
    exclude: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56518be30567e8057ee44cb46e6f916ae9f0c67fdb4fcd0b3f2e5eda69b2313e(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    instance_url: builtins.str,
    o_auth: typing.Union[MarketoOAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__801380782fb1f9681b6e6f5423656cf05c94ef570d51daa36920d39b1c56057f(
    account: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64a0405859705dce311d70baebb3bc505d535da9b60e5fdba7a7304025592485(
    *,
    client_id: _aws_cdk_ceddda9d.SecretValue,
    client_secret: _aws_cdk_ceddda9d.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d600bcb42bd2309d8a211399acb48b622ca7b46af03035c5555e3747e2ef2b59(
    *,
    client_credentials: typing.Union[MarketoOAuthClientCredentialsFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86263784684ceb950a00a13766dde95f979dfffada2529e1c69eb58d4b6c85cf(
    *,
    flow: typing.Union[MarketoOAuthFlow, typing.Dict[builtins.str, typing.Any]],
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeb8aa31cd135e4c5ed673ca30e70e83e3cd86d41801f9699ebb510885b962c9(
    *,
    object: builtins.str,
    profile: MarketoConnectorProfile,
    api_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1379032787009926181873ccc305a0955e2dd0d58473a4e17ec4430f0821186(
    org: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__011f223bbcc29a271af1ee4b50f8ca7ad6193b80b57bb4bf79ab8908466f4f6f(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    instance_url: builtins.str,
    o_auth: typing.Union[MicrosoftDynamics365OAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8268da092369f76bea8d817f9a7cc1d8dcbd2cecd8bc62823c2b8a09e5138ecf(
    *,
    token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93211fb9a48d02c2fdab04e73373bab19f2d26fa185f83be7274e93c2e19e291(
    *,
    refresh_token_grant: typing.Union[MicrosoftDynamics365RefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70b43b0200fa65d2295e51564572c42fc602eafb615e50fe451764dc9b3dc0dc(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    endpoints: typing.Optional[typing.Union[MicrosoftDynamics365OAuthEndpointsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    flow: typing.Optional[typing.Union[MicrosoftDynamics365OAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ae109d309d44a0e101cf414fca29def31504e79769a613872554b0a0d2b6fb7(
    *,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0e2926195df1e6dde7926b4f3ae2791126310b2c1e58f11485f1bc89e44f721(
    *,
    api_version: builtins.str,
    object: builtins.str,
    profile: MicrosoftDynamics365ConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0daf40ee42977120a5d3bc0ed71c20baf74dac7c3610abf7105cdc27386d8f02(
    tenant_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d26b7adf0fd56806c77413a8c33710b15aa17f977d91a0b02c4bfad24d438388(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    o_auth: typing.Union[MicrosoftSharepointOnlineOAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c44499b6b9db0006d3bd2b6d0016f0323662a961adc66eba56a2a83de73dc880(
    *,
    token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17dc0229e5b64936d4f7654c81ea06d1085aecfb20d954aa8ecfde4abe614d72(
    *,
    refresh_token_grant: typing.Union[MicrosoftSharepointOnlineRefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__716e62ba44f6f6a83bf1d88a18cdcf2063d3d613688088456b12654e5e384e2f(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    endpoints: typing.Optional[typing.Union[MicrosoftSharepointOnlineOAuthEndpointsSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    flow: typing.Optional[typing.Union[MicrosoftSharepointOnlineOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a0923fbe091b534d3a1ca8d9ba5097c24ea632b8fd07c4a6c57f8145d43b6ad(
    *,
    site: builtins.str,
    drives: typing.Optional[typing.Sequence[builtins.str]] = None,
    entities: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4a2d0ff5431cb6dd067791d63c4cdafd6c010289443e62713e19daf55335d75(
    *,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c5ba72fb01ff6d8aef9465671d0c5e3f4de630b3ad915e9a96ded987c4eedcd(
    *,
    api_version: builtins.str,
    object: typing.Union[MicrosoftSharepointOnlineObject, typing.Dict[builtins.str, typing.Any]],
    profile: MicrosoftSharepointOnlineConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9eea2823b899bd9f32f2a9d6ef72227e8b50a7af088cc1f940d8649c10c830e8(
    tenant_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a637938864a788d69acdfb22629eb81f7a59bfd0ae6a54ea8850a8c2452e7086(
    *,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9407225e27dbb4838ea7b03f43774d6a10e258ec3db30d4046317f81bc86197a(
    tasks: typing.Sequence[ITask],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e96aa6ca236dcbbffdd35eba014e3957a264c044051bae3dd2674912fb199e81(
    flow: IFlow,
    source: ISource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d0aa93167e776d8c97b0ea87e2dcf46b18ed3f17bee9a998bf24417176cac02(
    *,
    password: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d871624f397acc790fe4b2dff61b2c9af47bf80e85930bbc060e18210cf26a0(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    basic_auth: typing.Union[RedshiftConnectorBasicCredentials, typing.Dict[builtins.str, typing.Any]],
    cluster: _aws_cdk_aws_redshift_alpha_9727f5af.ICluster,
    database_name: builtins.str,
    intermediate_location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
    bucket_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    data_api_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__023bd631842c0c7e2507f9b94b65983b72d1ca7397b9d0e6eaa671613022e654(
    *,
    table: typing.Union[builtins.str, _aws_cdk_aws_redshift_alpha_9727f5af.ITable],
    schema: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26848c0b62c9c9752bc706327fec0a52eb543988fb667720c479490dd72e453c(
    *,
    object: typing.Union[RedshiftDestinationObject, typing.Dict[builtins.str, typing.Any]],
    profile: RedshiftConnectorProfile,
    error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bea771096082895a3b2fdb0a6ef285d5a6dcd168c3b1c7817b36f3d94483138(
    *,
    database: _aws_cdk_aws_glue_alpha_ce674d29.IDatabase,
    table_prefix: builtins.str,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcfab06fa3a7f71b0e7bb0a5d9ad3825206b0dd52d444967bdcb662797fbd338(
    *,
    location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
    catalog: typing.Optional[typing.Union[S3Catalog, typing.Dict[builtins.str, typing.Any]]] = None,
    formatting: typing.Optional[typing.Union[S3OutputFormatting, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a2f9712666e80398c9230f454c7c60b9bae2fac1dbb25be213d6ad5a917f82(
    *,
    file_size: typing.Optional[jsii.Number] = None,
    type: typing.Optional[S3OutputAggregationType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b6f8b75a73786f0e12a1a707e6c0214b9f2b1718fee0bc1bca7b4ae05c33642(
    *,
    type: S3InputFileType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e77dee49c84e2591524d02869bd5c43168a375fb8148cbbc25c2e89cc70ef607(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07222f7ad6e14c07d1c839889d580bf00d9a135a0c0da6a5dc9b6846a66c125f(
    *,
    format: typing.Optional[S3OutputFilePrefixFormat] = None,
    hierarchy: typing.Optional[typing.Sequence[S3OutputFilePrefixHierarchy]] = None,
    type: typing.Optional[S3OutputFilePrefixType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__647c5a42bd0a3abbe0881bec37a2f5f356717ea5a7051431c18f534fd0fafa8c(
    *,
    aggregation: typing.Optional[typing.Union[S3FileAggregation, typing.Dict[builtins.str, typing.Any]]] = None,
    file_prefix: typing.Optional[typing.Union[S3OutputFilePrefix, typing.Dict[builtins.str, typing.Any]]] = None,
    file_type: typing.Optional[S3OutputFileType] = None,
    preserve_source_data_types: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11add0251725b085f566155764021eaac6c26a1c71db654617abc2f9d41fc41d(
    *,
    bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    prefix: builtins.str,
    format: typing.Optional[typing.Union[S3InputFormat, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce4c0b0b2383996eec6cecc0c36fb286975bc25afe5c2b0daf63e6f4df264179(
    *,
    password: _aws_cdk_ceddda9d.SecretValue,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c30df13ceca2f1ff215e11a4e86a5f6bd8a1245b181c59827c0daa29e8f90072(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    application_host_url: builtins.str,
    application_service_path: builtins.str,
    client_number: builtins.str,
    logon_language: builtins.str,
    basic_auth: typing.Optional[typing.Union[SAPOdataBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    o_auth: typing.Optional[typing.Union[SAPOdataOAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    port_number: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d90d6697fd4914c63c12e96e1fa677de8b617deda9d68e06597a1162de72ff46(
    *,
    object: builtins.str,
    operation: WriteOperation,
    profile: SAPOdataConnectorProfile,
    error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    success_response_handling: typing.Optional[typing.Union[SAPOdataSuccessResponseHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da515d0d4648ceb542f575c8c56866e2466cb923c70d677cbc3a707ef221ccf4(
    *,
    token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cefed30b945239087f3dbb8a1ddb5dabb6307d3d35e04ede5e4a6887f6d0d581(
    *,
    refresh_token_grant: typing.Union[SAPOdataOAuthRefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fff92b1fecd8fb687b0fb4bdc1411cb80fac93d1dfb20791ff4b5c327fd3b240(
    *,
    client_id: _aws_cdk_ceddda9d.SecretValue,
    client_secret: _aws_cdk_ceddda9d.SecretValue,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6c602c5338ef47ca8f8b846c7354c60a34e2b2a3c774b4e8c0581d482e6294f(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    endpoints: typing.Optional[typing.Union[SAPOdataOAuthEndpoints, typing.Dict[builtins.str, typing.Any]]] = None,
    flow: typing.Optional[typing.Union[SAPOdataOAuthFlows, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46c8000b7de41ff27d29d18565fcd6f07d4e7be2d898c826689b0a5ee0cc9835(
    *,
    object: builtins.str,
    profile: SAPOdataConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ed6c082cacef689ea56d955987bb16bb38ebfbc22ac5a9953c1609643d6ef5(
    *,
    location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb386fe4c6e6ec8ddee55dea0effc0a7bd692124b527bb2ffbb3554ffd2a04ee(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    instance_url: builtins.str,
    o_auth: typing.Union[SalesforceOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    is_sandbox: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26af46d5b920211884966f102c2c1f731758b3a81197ca9ea732b4a377afecd4(
    *,
    object: builtins.str,
    operation: WriteOperation,
    profile: SalesforceConnectorProfile,
    data_transfer_api: typing.Optional[SalesforceDataTransferApi] = None,
    error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f99b5a5bb33f8ce8861da82005fc5c2a43bf5508c1b5c06cc8ca4e4a6d4105f8(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    instance_url: builtins.str,
    o_auth: typing.Union[SalesforceMarketingCloudOAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c57117565965b356b2a164ff026a738bf39d9737f2ca6fa64ed370537b81894a(
    *,
    client_credentials: typing.Union[SalesforceMarketingCloudOAuthClientSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96bd44a4c49d944fa430925f47eb270e0c8112c56b8100f96cefcfb18b121a1b(
    *,
    client_id: _aws_cdk_ceddda9d.SecretValue,
    client_secret: _aws_cdk_ceddda9d.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcff86daa0f6250709c4f5188043150713c1b07212980cb196f7953d27bbca74(
    *,
    token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2121dcb2c9866dc66748863d722c2e24692a091e9e083497b7e972827e5ec10f(
    *,
    endpoints: typing.Union[SalesforceMarketingCloudOAuthEndpoints, typing.Dict[builtins.str, typing.Any]],
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    flow: typing.Optional[typing.Union[SalesforceMarketingCloudFlowSettings, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fffd1efba2dc38fee00bedf5fe2bb6dd15b6a55e87350eafa49ced8cfdaa5d1b(
    *,
    api_version: builtins.str,
    object: builtins.str,
    profile: SalesforceMarketingCloudConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bb20287992df1bb2824bccc50aa824c16613f769993cb06ee2d3bd7bd25daee(
    *,
    refresh_token_grant: typing.Optional[typing.Union[SalesforceOAuthRefreshTokenGrantFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e4b4bc6fd4f76d44c56b32d530c5958a5d59603bbdcba534918f88312b2213(
    *,
    client: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    refresh_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b3d2312e8e6dbe607505cbf86b95e10be30b1477e042903f79af94a19fb24a6(
    *,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    flow: typing.Optional[typing.Union[SalesforceOAuthFlow, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30d372f25a17b9521a450436c8487a90f4bb05f9b654a2ae6047526cb28bc529(
    *,
    object: builtins.str,
    profile: SalesforceConnectorProfile,
    api_version: typing.Optional[builtins.str] = None,
    data_transfer_api: typing.Optional[SalesforceDataTransferApi] = None,
    enable_dynamic_field_update: typing.Optional[builtins.bool] = None,
    include_deleted_records: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0a2f97eb1106a2fa425f6885698e656218767d3d41fc35a8560b8aeec3a8720(
    *,
    end_time: typing.Optional[datetime.datetime] = None,
    first_execution_from: typing.Optional[datetime.datetime] = None,
    offset: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    start_time: typing.Optional[datetime.datetime] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35c555741db534372681a356953cf08bac7dc48ca53b011426d5a7eabe6b2255(
    *,
    password: _aws_cdk_ceddda9d.SecretValue,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63673f65488910421fc09fc00bac26db0a7f26ac179c42060b98bec55fec912e(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    basic_auth: typing.Union[ServiceNowBasicSettings, typing.Dict[builtins.str, typing.Any]],
    instance_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad25ad6831ab64e0fadd9ceeda1adc39130b601638da4a9cdd3e82d64afbb722(
    domain: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed901b4674fdd5b5d8aca2d28fbdf744d228510b752e4514767f32208c2ffc3(
    *,
    object: builtins.str,
    profile: ServiceNowConnectorProfile,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3366bcfa4a8faf3ddcc2d8352e6dcdb18f40aaa06c7029081e80039b2777ad0(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    instance_url: builtins.str,
    o_auth: typing.Union[SlackOAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb08209450125f2e8479d608154ce728f1d90ffdbfc2b59d68cbe461fc268983(
    workspace: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c85d508ca7011bdf2ded0cf3b5e9fdc6fcc5539051311b7c2170f93564ea838(
    *,
    access_token: _aws_cdk_ceddda9d.SecretValue,
    client_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    client_secret: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0e4d776743bda8a375dea1e95823dd583e550a30280bd3b02143312f8d17cec(
    *,
    object: builtins.str,
    profile: SlackConnectorProfile,
    api_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d7db9d78ada1829fc032eed083a5d0fe61002cd2949f410b164b6a2aa8d19a7(
    *,
    password: _aws_cdk_ceddda9d.SecretValue,
    username: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__741297c13658831cfda5a41ceb6e41a3d0a3f3ab7415a9950c3d342ae37f2ab7(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    account: builtins.str,
    basic_auth: typing.Union[SnowflakeBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
    database: builtins.str,
    location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
    stage: builtins.str,
    warehouse: builtins.str,
    integration: typing.Optional[typing.Union[SnowflakeStorageIntegration, typing.Dict[builtins.str, typing.Any]]] = None,
    region: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98eee9aad789e1c5f53d3d3a38169512e40be7865c4c7cce212218790009d32e(
    *,
    table: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f80b375007188911005c4fd1c96aa7c040f5466ec3e3d70f49b5dbf3e6462687(
    *,
    object: typing.Union[SnowflakeDestinationObject, typing.Dict[builtins.str, typing.Any]],
    profile: SnowflakeConnectorProfile,
    error_handling: typing.Optional[typing.Union[ErrorHandlingConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8e0ca5f0d4687c015b4915a3dac207a7de1a514c0f968248ed4dec2a6c8d2ac(
    *,
    external_id: builtins.str,
    storage_user_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24692fc26478ce2d71b63bb5cb3aad2dce8ab876ef9bcb1fe29cc22712b96603(
    type: builtins.str,
    source_fields: typing.Sequence[builtins.str],
    connector_operator: typing.Union[TaskConnectorOperator, typing.Dict[builtins.str, typing.Any]],
    properties: typing.Sequence[typing.Union[TaskProperty, typing.Dict[builtins.str, typing.Any]]],
    destination_field: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6128ea3ff1cb4e2e28beece9552596b5334b2f91d87f23bc6895ad8e3da19705(
    _flow: IFlow,
    source: ISource,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c287db748553ab89efc05e6ed00d913c713709726c7d10b4844f66cba313313d(
    value: TaskConnectorOperator,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0eeab5d21f2d3f7741e64d02a9bdad89aeeaf57cd56a47a04c058b099d1e6649(
    value: typing.List[TaskProperty],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f40185ac47e4693214d2d99ed5b935e3499b032a5920f9938a3c72fb8e6270de(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e9446eb1c419044c87ad7f9339e6287c76df820ed89f50bab39f0059b3d6b50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ba0519612063188a23f4ad3daf76a759533cfc1addfd48d040e60b2e3d6a1cf(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398aead5d0bd8510768d3927e715f426a75f799690a7ec9da8469770e0170e2b(
    *,
    operation: builtins.str,
    type: typing.Optional[ConnectorType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1b051bd387400fdca98fdb91ffc4aaf76026ad8dbe494f487221d94253d9472(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87a06aecfdef9894d45526cc1334c77d31cee6f12306317692baa83368d553f4(
    tasks: typing.Sequence[ITask],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c41a4351b279826717987e6ab9ce3182aa8f0612255630693a7292c8744f81ae(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    mask: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2acd39d37b83d498dba9046e8062304f5227103f50f8d473a9413c6e51236421(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    length: jsii.Number,
    mask: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2550ec4dead61e5b0ae4ece8179540f94ded48f2beb2242305d9d547b7f1070(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    length: jsii.Number,
    mask: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c32903e226b3cb4c5abb8f003faf20da66d939c849a4e3f6437bfa9f15338d65(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    length: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08b0d9faa4910c0e23d0378d533d86a82930a2a943b1df1a232d4069514d2b44(
    *,
    properties: typing.Optional[typing.Union[TriggerProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a5595e28b343c24db0c5791c565077bcd1fc6f83d998a876f019a80cc3446ce(
    *,
    data_pull_config: typing.Union[DataPullConfig, typing.Dict[builtins.str, typing.Any]],
    schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
    flow_error_deactivation_threshold: typing.Optional[jsii.Number] = None,
    properties: typing.Optional[typing.Union[ScheduleProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__881f3c09d75b30ebfa1052386ec4d818fbe77108f41bdb330c146010693f9340(
    *,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
    auto_activate: typing.Optional[builtins.bool] = None,
    status: typing.Optional[FlowStatus] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17d0a7e0c9f7824af925917ebf8638687c5bf11d56459938477e76a6833a4f99(
    condition: ValidationCondition,
    action: ValidationAction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67ca94b43da0f5239fa9d3debb200cfc239bda03c2ab5cb6a652e0f81f7f9ddc(
    condition: ValidationCondition,
    action: ValidationAction,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ab11a20a421606aa4a75efad2710edf490193982d06bdda848e63e5004916e(
    action: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fa951e67892a14eb66e58a134d78cd121a89409ae405b3fc282424907374786(
    field: builtins.str,
    validation: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e358a270bee6e0250a4fef9ab13c1d9fd629976d950a828b4c6095617faeb739(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8660955800816a63c713edf4cedc6b5bd3f8508158ed48f3f1bcb93963ed86ee(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ca5f819a7a2769713267e5a06a363b02303fc7a02563ad63b427b398c8b0ce2(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2367c161e7bef9cf940a0f0d217ab26c89c27654335b8fdf1a4fa4174c76a3ed(
    field: typing.Union[builtins.str, typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73f7b1adeb34e5db29fb94883369e879db3c560d15a3780e96a8395a83c68ae5(
    type: WriteOperationType,
    ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1615e1c8b7a88521ec7bb5582944e3d891389ab5133988adb27665eb301f8d5(
    ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac64bd6fc67a5fb99235ed0ba6ef9ad8d078a017d9a4fcf2b238594332ddcc1(
    ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3745e4221919777d18492c9ab67350b540cd9a81943c1786bc5a732333892140(
    ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a768fe8cad0fc8d76119bf36b0b0901ed4f1e02a778804c973adea107c099606(
    ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__793b9e17c548f9557156ccc9f70fad08825c498ddd0d139a291e99df30fa18f0(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    instance_url: builtins.str,
    o_auth: typing.Union[ZendeskOAuthSettings, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c702d5690575e12254d4754078c852e743427c9206579bb48a06e3969a46b9f7(
    account: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85f74bf49c07fa8e80d2caf3ebf8f612482134e20074260644582a8666e89eb7(
    *,
    client_id: _aws_cdk_ceddda9d.SecretValue,
    client_secret: _aws_cdk_ceddda9d.SecretValue,
    access_token: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12d6ac01e1819517b8f5ade63157f0ddc52a9c21ef9ffb1337daaf1d72b859b4(
    *,
    object: builtins.str,
    profile: ZendeskConnectorProfile,
    api_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06579ce6121216cc8ffcacfabfa42d87b49a8b42d2f2dd0d6bf18a19940a8c77(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    basic_auth: typing.Union[AmazonRdsForPostgreSqlBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
    database: builtins.str,
    hostname: builtins.str,
    port: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89b05a676f3a85bf2b6f7814749de8f4991e610d071aed5d693f8a732d12d900(
    *,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    pat_token: _aws_cdk_ceddda9d.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f41824d4d0e7e596b73b8964ae3c9323e7ac9e57fc2490edce69fc33b58e525(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: typing.Union[ConnectorProfileProps, typing.Dict[builtins.str, typing.Any]],
    connector_type: ConnectorType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88ce195d30a4f9a428558674e3292dbaa455820c183acaffd9afb1e9718e87ab(
    scope: _constructs_77d1e7e8.IConstruct,
    resource: typing.Optional[typing.Union[builtins.str, _constructs_77d1e7e8.IConstruct]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b56531af8c41eed5beccf6a33a61319cd682a85bbf2967c237fc17d06f31a5d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    type: FlowType,
    status: typing.Optional[FlowStatus] = None,
    trigger_config: typing.Optional[typing.Union[TriggerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f3c65eebc4f29cf16125ffb6702a331f9a79ae1812e08301259b59c02859425(
    metric_name: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2acf34eacdae40710a13c3ed45f83158f59e3e15966b80313d67d608ba9ee3a(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f03f9a11b1059cab6d66afc004104a59693f30bd1d46f2cbc04ed46840517563(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__898943b33b4140f7380992a94ce5f3f39a5d95bf03491505dc4cb95af4a7de3e(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35de0ceeba864e70ecbbe43f5c1d7bece48df28eda3b3a6792c125eaa4810523(
    *,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
    type: FlowType,
    status: typing.Optional[FlowStatus] = None,
    trigger_config: typing.Optional[typing.Union[TriggerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f9e401efb1d1cbb7beb077ff01c665cdd93baa94ed7115889fb572273e3f077(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    basic_auth: typing.Optional[typing.Union[GitHubBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    o_auth: typing.Optional[typing.Union[GitHubOAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d92d1f337d55056eee44e5cb4fc8d5f572fb6f21a410c420029a743dfde292e8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__024d255b0faaeb3d18d0d1d30c2700693bab2b18eee0319a5fd82f6e0bd134ab(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f86afff4e70e3f5322709dd23ddff9112e2c6439819db87fb1570f05121e4ae7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_version: builtins.str,
    developer_token: _aws_cdk_ceddda9d.SecretValue,
    o_auth: typing.Union[GoogleAdsOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    manager_id: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5886bd104fbcfbee5a5e13271dc65eba692c4b203fd7e3b57dd534758876df5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd36306e21ad794d3ad49d35c157d4d1c59dabbe31a3d5d925442192131c8fc9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c43bd6b69bc3bf59de5b391f25cdf12b469de365ed8de5be512e17a271f7045(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    o_auth: typing.Union[GoogleAnalytics4OAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__637fbb37964ed107f6b98fa3a2364d0015e3f062ded5c0ed3cdbd4b1f9d2bce4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eafc7f7b62ebd94da254cb5bcd21396d7915c304471032e3ada0d238287b38d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea31aa0261671f54af7beec877efbbf33709316e870e74cca3c7de97b6da90e9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    o_auth: typing.Union[GoogleBigQueryOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34bd60074077ce74fb7dfee3d50fc4565c5c9a4944714c75ec6b392fd46705b0(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9f13077418355c76fb5cfa27ee04588c7082264956de751c0d05bdf9038224(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2136d4559db32f0e5755749dec96f0202761cc14f7e5dd4c10f5c2c5fc15aa(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    o_auth: typing.Union[HubSpotOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0319dd9c8a5d2e3bee2c855238214cb1a8f4a38b759b49f5fe258829cc35aa3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14884df6d2e23cdfeecd9992ccb92d81f2dfcf150f24e3d572fd294238c3fe83(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__763c41122983019c457da20c45fe1dfbbca1c1449cc69b4c8b816e2a90d82e4d(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0164bc87a394237879abd8ee65e72956a291ed0eea1cc44de9736e00403baf94(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e32deb023fd1da8653ae939d2fc08254ee0ded96f4e39571b669df7c596e4a01(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    basic_auth: typing.Union[JdbcSmallDataScaleBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
    database: builtins.str,
    driver: JdbcDriver,
    hostname: builtins.str,
    port: jsii.Number,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdead6c1e387618dbc67702ba3c746da0fd7d293156ff0daec657685e2f61dd9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc97d291eeff1c6c890723e428dd35fda34ec527efa1cdd1e7b2b2ca04bfb706(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17c85e4f48690fbb00d1604ff53a4fedbdbe8249687c1ef7c84e32fd1685bb2b(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de9b2b10ed2a04588baf16c32519a05254225651f4c460d9c5e32f6fb697d829(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    api_key: _aws_cdk_ceddda9d.SecretValue,
    instance_url: builtins.str,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fab62bc82e71cddf5bdb22f9430f2124a811b6af45e84d43ee08202bbd6631a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__065bdf7524e5dbd428b95d00e42375bf860b0486f0995251e8b669ec6ac9c3c6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a299aad732300797f33efd78c0a733afbf3e2e4abbd46ee3cc8968e60fc1712(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a678dcca6d941420e56a333102b5a0cb8c0d803561d5d835f4240c199f4ac4(
    tasks: typing.Sequence[ITask],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__630b751d36137c5140a0419a292ad559adbdbce0d246c34f18852346385b0037(
    source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    *,
    name: builtins.str,
    data_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07c247ea317fe5c6eb58ff91f5ca6af9502cac12e56792a5520cbfc4c32c9906(
    from_: typing.Sequence[typing.Union[Field, typing.Dict[builtins.str, typing.Any]]],
    to: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    format: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05f84f4f0f748a86f5d549f6eac81d409450ea2ef0c46d42e725684c6af1e306(
    source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    *,
    name: builtins.str,
    data_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebd0fbf617c72b22af5dfe5b02f0f6887532b0c433b7f704339b58b5d6a7ae0c(
    from_: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    *,
    name: builtins.str,
    data_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bf1b53973e5a4d28322754dfc146a010b77fd30692723b8a3d783a96a654674(
    source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    *,
    name: builtins.str,
    data_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bf0b9669a6a99c327db9986a7b753319745c897c65990576a333bf3f9577239(
    source_field1: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    source_field2: typing.Union[Field, typing.Dict[builtins.str, typing.Any]],
    *,
    name: builtins.str,
    data_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5374e74f303d3b208f61404b21a2141f422ebc73c4c55c1c0bb9d56dca830409(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_url: builtins.str,
    o_auth: typing.Union[MarketoOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6719326a52f679caeaf4ee763bcdf20b57cc3721fec1de6baeb25dbd6e04cedc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__751aa592c50e735ef9492028fdd783baf185fdd81dae3a88fa20ac5a43ffda41(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d526fba10eba772302583964eed0ad031f9fc46796a3930b26ee72d6f7354e64(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0bb0eefccf75f7bb468f88528c6c7c0c3cfa07f29f4a753c32612c5e663b09d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_url: builtins.str,
    o_auth: typing.Union[MicrosoftDynamics365OAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95f695492e2672da02edd0d068b199a21c837fdb72221a49705e0813d22f4285(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d547be811c4253a9a7e978e6ed046e654cd132030758eeba17df89bab759499(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ee08ed5ce759617974eb4dc1e5a90ddf403380044aa2a667eee9212b5da103(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e8e4b0913b75c925eb456a841b29ed60151ccce3d9dad6b2c9cd15845a6268a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    o_auth: typing.Union[MicrosoftSharepointOnlineOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03b3073f8f9e06a602e324649deab60e7b7dd73a8d582c81d4515d58a0e7e191(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76c71d094d3248d78f6f3e713946ba72ca8b0809bf263a4154c236b53cc3e41e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c759b75072354d63580102008aa08f507d648d1438edd61d1dd8c93bda750d2d(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdd05f239f7e2082c835f28f1395f4cd46f69d24e3fc862cd99eddfd8bf951b6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3de51d773e1730010fdf7bfeffbbc6e0aa2ec00de7959b616230568433da3b3d(
    *,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
    auto_activate: typing.Optional[builtins.bool] = None,
    status: typing.Optional[FlowStatus] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d3b83aa54f4b21125bcd8395900d743242af7f296f98624a1512d760b575410(
    *,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
    auto_activate: typing.Optional[builtins.bool] = None,
    status: typing.Optional[FlowStatus] = None,
    pull_config: typing.Union[DataPullConfig, typing.Dict[builtins.str, typing.Any]],
    schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
    schedule_properties: typing.Optional[typing.Union[ScheduleProperties, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a58ef0e10db44b1b1bf9a8290423bc02cb64eed592a0f44d8f14f809ad3d0ad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    basic_auth: typing.Union[RedshiftConnectorBasicCredentials, typing.Dict[builtins.str, typing.Any]],
    cluster: _aws_cdk_aws_redshift_alpha_9727f5af.ICluster,
    database_name: builtins.str,
    intermediate_location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
    bucket_access_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    data_api_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4dd394b83ad709efa3566a77735fda086d2c8dfc273aeeccb14a570800fa0e5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2278df91381897b463bd0b4bfb4b8dbcaf0ee452cb603acb731230cfde5974cd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4b4b06cb0cb403843553ae93654f4667c11e8d1be7a5f6df39b0bc7265893d3(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5862768538371b3073f16756f588d1e5dda667285c69b64f9f36b872298e0ba(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1e09e5f5312a9f8751cf5ce9d37ff5134334869d46594888883266c8504ea46(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1456a6c00e75acdfb46d10ac9e74fd8a326dbbb53336209c40da1bf1772dc678(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    application_host_url: builtins.str,
    application_service_path: builtins.str,
    client_number: builtins.str,
    logon_language: builtins.str,
    basic_auth: typing.Optional[typing.Union[SAPOdataBasicAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    o_auth: typing.Optional[typing.Union[SAPOdataOAuthSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    port_number: typing.Optional[jsii.Number] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6386649257a15b140d1f567e872eeeee4f4afe56bbb09734eb8b164e005830(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65d328d60d5002bf9c8a09117a27e9b1e946b48879e17ad76aba5c6fd23857c8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be9c75208a53ebc4db44ac27cc9aaac34a0b9ac8e574e73ff8a4a30fa1b7b46c(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0026fc92ed92f4c9cabaa7c920e2d283ecacf980920ee014d8bef28dfb74a01a(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__971cdd11384ff73d58d6d421eac3224b366d50d8ce1505049b566c9100872982(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_url: builtins.str,
    o_auth: typing.Union[SalesforceOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    is_sandbox: typing.Optional[builtins.bool] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e9cb36a47dea6920a365a064afad384a739bd0c19f1536826167577529e475d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6143d77fe422945c9a8f9f82025a860f0b13de560638015c9163a5a9040ca095(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dee9194e1f6c5e09118515e69827c61c083ee45cb92df1fbfc9892e9d54ff75f(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8410f844ea9b96fa7a6e2f3518a5fec1a35a25a685a6fd7e2aa919f6daf34a69(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_url: builtins.str,
    o_auth: typing.Union[SalesforceMarketingCloudOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dfe81c83ad5453bac6f9afed24e1092edd26038b0f26f9a7715823dd6be9013(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10e4e0603463cd481a8c7c66d1a2ae2e258c5f30a96ad40831f438aeb5714ab2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56dbfc65e9095e0421b0e95f214dc50199e598e4172ae2acb02d9ded12082332(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d75665b942bd54e4d796605d1783ec9b72c14a580d2a0908e9cb1017bb7043d6(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b3879038be1a4e5f7230bc71ada45cc46a2e95edf8846a895bce14e71525254(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    basic_auth: typing.Union[ServiceNowBasicSettings, typing.Dict[builtins.str, typing.Any]],
    instance_url: builtins.str,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc536210ddd6cc47417ce5407ff85ce1a78d932f268015124e63190beb683f52(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d74eb3f8c13441d3702ed399f4902f3d927af2d3fb1f3a56058885640d44c856(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e637407ea094bc9b64340ae13ad48f098c55d05718b6aec5a8e34f6b74c96748(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0128d0be60f75daae2247525587b1088f9493b303433c0e91bf36df088f1cdc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_url: builtins.str,
    o_auth: typing.Union[SlackOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6d7be495d76a6378875da67c6db9335aa8809f0d4212fa3571d8f36bcef7a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d301278adbfbe76bb9432169d16b9329b86fc9f8c67b465a86f02c352e56c443(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a922546c73247e33c6ba160429e170e96058ecb38cef1fcdf8eb5e60c72bbc66(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dd1063a040290a9477ba77cf2296e4ada3d8751608122952462320895016dd5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: builtins.str,
    basic_auth: typing.Union[SnowflakeBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
    database: builtins.str,
    location: typing.Union[S3Location, typing.Dict[builtins.str, typing.Any]],
    stage: builtins.str,
    warehouse: builtins.str,
    integration: typing.Optional[typing.Union[SnowflakeStorageIntegration, typing.Dict[builtins.str, typing.Any]]] = None,
    region: typing.Optional[builtins.str] = None,
    schema: typing.Optional[builtins.str] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e45fdc5fb210a90226ec328404153f805b74ea3af4d92b750e7a7b8a0a540eb5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e8b5f134e73c7420c208bd3ac5f610bc4e9b20cbac0e9ae51f3a8f40cd09921(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97be675a19891adcd3ba67bd78ff2033e0c6f9cf115d622f3d48b237299426ea(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13e29f4a8761d1eafa730da5c88359c07635eb7cd018ce40a9576c09b4f70b53(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    type: FlowType,
    status: typing.Optional[FlowStatus] = None,
    trigger_config: typing.Optional[typing.Union[TriggerConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2ad24e9750ce2b71d025e53bf1a90ab832d3b3158aa3c1d1b6854448d97223b(
    auto_activate: typing.Optional[builtins.bool] = None,
    status: typing.Optional[FlowStatus] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95dacf4b74f5f17ded6d934b31d52c2f28e41c83bb0b5473ad280d31b95e888b(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d87ab1118f8aac7fd9553e0cec17f7aa9bdde8eb8268a14bb2dab10e12e5572b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_url: builtins.str,
    o_auth: typing.Union[ZendeskOAuthSettings, typing.Dict[builtins.str, typing.Any]],
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a01eaa845aed42a839b2acc7400a2b64541982442ebece58ad0f08f47078a424(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cc9bb96eacc438143c77942ba4c355dc1966ea85ac7a73bdb610d472467138f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2097f06da6031382a5fcb7073e896e199a7e0bd4857a9865d1fcc4aaf0fc891d(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__598bab69fc3c82125f6db3d072992382b187be9b68dd22b799f9391166cf138c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    basic_auth: typing.Union[AmazonRdsForPostgreSqlBasicAuthSettings, typing.Dict[builtins.str, typing.Any]],
    database: builtins.str,
    hostname: builtins.str,
    port: typing.Optional[jsii.Number] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1068ccf524cfa09953853645fd0d3ad1292f24c43170d6785a588eaa0bc8cc76(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1927661bcb638d1a9f5a24011091984bce47f46d3ab478605a61a7bc7ebcdf8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5d92b91aa48252ae6085ca88803bb9621caf7e8f0b9a83834348de26d8f497c(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a58bdbd0832b8777a6069753afb1fb46c89bf3b05a095268a3c14431bd1adde(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    pat_token: _aws_cdk_ceddda9d.SecretValue,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cfdc6017db78a12701ec0c2cc86ea3ba126285b5ac69bb179086503f6b06191(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bff0c5e2bcd9170090e9693991889256002bf6328945d0f4773bf532282213fd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bde8e7c5e26495b30b4764f5ede134b7ed0c22527dd3faff8410c0120a1a93b4(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2f47cdd9c92993f8180f795883ea922561afaaf0dd29d1fcc7149fc980816b(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1838c353b79166cff9f0c099c3a545db7b0fc4a6bdf92a753c8c0555355f1d7(
    condition: FilterCondition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dc11e36c8e97ec161cf0e41e354e44678d3c7f9493a45862d7e905722153c42(
    condition: FilterCondition,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f7df3fd64b76749dce46b072eb594c695bd5beebbe16ce8da249163dadc67e2(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff3d2380df317e993005c128fbb6bbacadcada6d54f259f89a3387f9d3f739e6(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cd876dce9ba6511ecfc8571441244f3a14d9352d9abfe9a597cf724a29014b1(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d5edd63aaccd54eeb9f7c31e4ec6387af3a10d4f0415ee5a2af8d6f3346b564(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3076a4259c391aa8bfde0da045072f7e3d60236ba8ab4932330853b7819380bf(
    flow: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac553b95617d60e3e759e601d3adb0a1316d00975c3171e9d0d0cc95d2ed9f34(
    scope: IFlow,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87a164f0be4a5d75d7089b4df6855c5ff83e9019490cd7856fab5d7232ac6f52(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    auto_activate: typing.Optional[builtins.bool] = None,
    status: typing.Optional[FlowStatus] = None,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b205dc908b59be5756e8804a9db3a2e274c5f0bed7a9f1686c9874eabfe4b34f(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e905b80fb14b8a853fdbaf13a24111c841b000e327e3dd51c5655dbf8bdc8ff4(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14c889972d22be3a8c6b6f8373772766c112b75ebbd835bd5653c7494e51d7df(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    pull_config: typing.Union[DataPullConfig, typing.Dict[builtins.str, typing.Any]],
    schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
    schedule_properties: typing.Optional[typing.Union[ScheduleProperties, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_activate: typing.Optional[builtins.bool] = None,
    status: typing.Optional[FlowStatus] = None,
    destination: IDestination,
    mappings: typing.Sequence[IMapping],
    source: ISource,
    description: typing.Optional[builtins.str] = None,
    filters: typing.Optional[typing.Sequence[IFilter]] = None,
    key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    name: typing.Optional[builtins.str] = None,
    transforms: typing.Optional[typing.Sequence[ITransform]] = None,
    validations: typing.Optional[typing.Sequence[IValidation]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3ad6452763aac3ac2da51fd43dd4b8dc75fe17b124c46e8b1456763d41cf6ba(
    id: builtins.str,
    *,
    target: typing.Optional[_aws_cdk_aws_events_ceddda9d.IRuleTarget] = None,
    cross_stack_scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    description: typing.Optional[builtins.str] = None,
    event_pattern: typing.Optional[typing.Union[_aws_cdk_aws_events_ceddda9d.EventPattern, typing.Dict[builtins.str, typing.Any]]] = None,
    rule_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IConnectorProfile, IDestination, IFilter, IFlow, IMapping, IOperation, ISource, ITask, ITransform, IValidation, IVertex]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
