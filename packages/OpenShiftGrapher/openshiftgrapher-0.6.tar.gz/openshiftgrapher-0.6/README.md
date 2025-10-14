# OpenShift Enumeration

OpenShiftGrapher is used to enumerate OpenShift clusters.  

## OpenShiftGrapher

### What it is

The script is mean to create relational databases, in neo4j, of an OpenShift cluster.  
It extracts objects and relationships for information like projects, service accounts, SecurityContextConstraints and others.  
The neo4j query system can then be used to spot inconsistency in the database that could lead to vulnerabilities.

![alt text](https://github.com/maxDcb/OpenShiftGrapher/blob/master/media/general.png?raw=true)

### Installation

#### Option 1 — Install from PyPI

Using pip:

```bash
pip install OpenShiftGrapher
```

Using [Astral's uv](https://docs.astral.sh/uv/):

```bash
uv venv .venv
source .venv/bin/activate
uv pip install OpenShiftGrapher
```

#### Option 2 — Install directly from GitHub

To install from the GitHub repository:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install git+https://github.com/AmadeusITGroup/OpenShiftGrapher.git@main
```

#### Requirement

The script needs to communicate with the neo4j database, and the OpenShift cluster in python.

To install the neo4j database we recommend to install neo4j desktop, which contain the database and bloom for visualisation:  

https://neo4j.com/download/  

### Usage

Then script can be launched with the following command:  

```bash
OpenShiftGrapher -h
usage: OpenShiftGrapher [-h] [-r] -a APIURL -t TOKEN [-c COLLECTOR [COLLECTOR ...]] [-u USERNEO4J] [-p PASSWORDNEO4J] [-x PROXYURL] [-d DATABASENAME]

Exemple:
        OpenShiftGrapher -a "https://api.cluster.net:6443" -t "eyJhbGciOi..."
        OpenShiftGrapher -a "https://api.cluster.net:6443" -t $(cat token.txt) -c all -d customDB -u neo4j -p rootroot -r
        OpenShiftGrapher -a "https://api.cluster.net:6443" -t $(cat token.txt) -c SecurityContextConstraints role route

options:
  -h, --help            show this help message and exit
  -r, --resetDB         reset the neo4j db.
  -a APIURL, --apiUrl APIURL
                        api url.
  -t TOKEN, --token TOKEN
                        service account token.
  -c COLLECTOR [COLLECTOR ...], --collector COLLECTOR [COLLECTOR ...]
                        list of collectors. Possible values: all, project, SecurityContextConstraints, sa, role, clusterrole, rolebinding, clusterrolebinding, route, pod 
  -u USERNEO4J, --userNeo4j USERNEO4J
                        neo4j database user.
  -p PASSWORDNEO4J, --passwordNeo4j PASSWORDNEO4J
                        neo4j database password.
  -x PROXYURL, --proxyUrl PROXYURL
                        proxy url.
  -d DATABASENAME, --databaseName DATABASENAME
                        Database Name.
```

```bash
OpenShiftGrapher -a "https://api.cluster.net:6443" -t $(cat quota.token) -c all
```

### Exemples of Queries


```
MATCH (n:AbsentServiceAccount {name:"servicenow-sa"}) RETURN n LIMIT 25  

MATCH p=(n1:Project) WHERE NOT (n1.name =~ ('openshift.*') OR n1.name =~ ('test'))  RETURN p LIMIT 25  

MATCH p=(n:AbsentServiceAccount {name:"servicenow-sa"})-[]->()-[r:`HAS CLUSTERROLE`]->() RETURN p LIMIT 25  

MATCH p=(n1:AbsentProject)-[r1:`CONTAIN SA`]->(n2:AbsentServiceAccount)-[]->()-[r2:`HAS CLUSTERROLE`]->() RETURN p LIMIT 25  

MATCH p=(n1:AbsentProject)-[r1:`CONTAIN SA`]->(n2:AbsentServiceAccount)-[]->()-[]->()-[r2:`get`]->(n4:Resource) WHERE (n4.name =~ ('secrets')) RETURN p LIMIT 25  

MATCH p=(n1:Project)-[r1:`CONTAIN SA`]->(n2:ServiceAccount)-[]->()-[]->()-[r2:`get`]->(n4:Resource) WHERE (n4.name =~ ('secrets')) RETURN p LIMIT 25  

MATCH p=(n1:AbsentProject)-[r1:`CONTAIN SA`]->(n2:AbsentServiceAccount)-[]->()-[r2:`CAN USE SecurityContextConstraints`]->() RETURN p LIMIT 25  

MATCH p=(n2:AbsentServiceAccount)-[]->()-[r2:`CAN USE SecurityContextConstraints`]->() RETURN p LIMIT 25  

MATCH p=()-[r2:`HAS CLUSTERROLE`]->()-[r1:`create`]->() RETURN p LIMIT 25  

MATCH p=(n1:Role)-[r1:`create`]->() RETURN p LIMIT 25  

MATCH p=(n2:ServiceAccount)-[]->()-[]->(n1:Role)-[]->() RETURN p LIMIT 100  

MATCH p=(n2:AbsentServiceAccount)-[]->()-[]->(n1:Role)-[r1:`create`]->() RETURN p LIMIT 100  

MATCH p=(n1)-[r2:`CAN USE SecurityContextConstraints`]->(n2) WHERE NOT (n2.name =~ ('acs-splunk'))  RETURN p LIMIT 25  

MATCH p=(n1)-[r2:`CAN USE SecurityContextConstraints`]->(n2) WHERE NOT (n2.name =~ ('acs-splunk.*'))  RETURN p LIMIT 25  

MATCH p=(n4:Resource) WHERE (n4.name =~ ('secrets')) RETURN p LIMIT 25  

MATCH p=(n1:Project)-[]->(n2:ServiceAccount)-[]->()-[]->(n3:Role)-[r1:`*`]->(n4:Resource) WHERE NOT (n1.name =~ ('openshift.*') OR n1.name =~ ('test'))  RETURN p LIMIT 25  

MATCH p=(n4:Resource) WHERE (n4.name =~ ('.*bypass.*')) RETURN p LIMIT 25  

MATCH p=(n1:Project)-[]->(n2:ServiceAccount)-[]->()-[]->(n3:Role)-[]->(n4:Resource) WHERE NOT (n1.name =~ ('openshift.*'))  RETURN p LIMIT 1000

MATCH p=(n1:Project)-[]->(n2:ServiceAccount)-[]->()-[]->(n3:Role)-[]->(n4:Resource) RETURN p LIMIT 1000

MATCH p=(n1:Project)-[r1:`CONTAIN SA`]->(n2:ServiceAccount)-[]->()-[]->()-[r2:`get`]->(n4:Resource) WHERE (n4.name =~ ('secrets')) AND NOT (n1.name =~ ('openshift.*')) RETURN p LIMIT 200  

MATCH p=(n1:Project)-[r1:`CONTAIN SA`]->(n2:ServiceAccount)-[]->()-[]->()-[r2:`create`]->(n4:Resource) WHERE (n4.name =~ ('namespaces')) AND NOT (n1.name =~ ('openshift.*')) RETURN p LIMIT 200  

```

### SA not in openshift* project that can use SecurityContextConstraints

```
MATCH p=(n1:Project)-[]->(n2:ServiceAccount)-[]->()-[]->()-[r1:`CAN USE SecurityContextConstraints`]->() WHERE NOT (n1.name =~ ('openshift.*'))  RETURN p LIMIT 100
```

### SA not in openshift* project that has cluster role that can read secrets

```
MATCH p=(n1:Project)-[]->(n2:ServiceAccount)-[]->()-[r1:`HAS CLUSTERROLE`]->()-[]->(n4:Resource) RETURN p LIMIT 25  
MATCH p=(n1:Project)-[]->(n2:ServiceAccount)-[]->()-[r2:`HAS CLUSTERROLE`]->()-[r3:`get`]->(n4:Resource) WHERE (n4.name =~ ('secrets')) AND NOT (n1.name =~ ('openshift.*')) RETURN p LIMIT 200  
```

## Potential vulnerability

It happens that cluster is deployed with preconfigured template automatically setting Roles, RoleBindings and even SecurityContextConstraints to service account that is not yet created. This can lead to privilege escalation in the case where you can create them. In this case, you would be able to get the token of the SA newly created and the role or SecurityContextConstraints associated. Same case happens when the missing SA is part of a missing project, in this case if you can create the project and then the SA you get the Roles and SecurityContextConstraints associated.

### Absent SA that can use SecurityContextConstraints

SecurityContextConstraints can be given by role binding or directly:

```
MATCH p=(n1:AbsentProject)-[]->(n2:AbsentServiceAccount)-[]->()-[]->()-[r1:`CAN USE SecurityContextConstraints`]->()  RETURN p LIMIT 100 
MATCH p=(n1:AbsentProject)-[]->(n2:AbsentServiceAccount)-[r1:`CAN USE SecurityContextConstraints`]->()  RETURN p LIMIT 100
```

### Absent SA that has cluster role

```
MATCH p=(n1:AbsentProject)-[]->(n2:AbsentServiceAccount)-[]->()-[r1:`HAS CLUSTERROLE`]->() RETURN p LIMIT 100  
MATCH p=(n1:AbsentProject)-[]->(n2:AbsentServiceAccount)-[]->()-[r2:`HAS CLUSTERROLE`]->()-[r3:`get`]->(n4:Resource) WHERE (n4.name =~ ('secrets')) AND NOT (n1.name =~ ('openshift.*')) RETURN p LIMIT 200  
```

### Absent SA that has role binding in another namespace than their own

```
MATCH p=(n1:AbsentProject)-[]->(n2:AbsentServiceAccount)-[r1:`HAS ROLEBINDING`]->(n3:RoleBinding)-[]->() WHERE NOT (n1.name =~ n3.namespace) RETURN p LIMIT 100   
```

### Absent SA that can bypass kyverno

```
MATCH p=(n1)-[]->(n2)-[r1:`CAN BYPASS KYVERNO`]->()  RETURN p LIMIT 100 
MATCH p=(n1:AbsentProject)-[]->(n2:AbsentServiceAccount)-[r1:`CAN BYPASS KYVERNO`]->()  RETURN p LIMIT 100 
```

### Gatekeeper whitelist

```
MATCH p=(n1:GatekeeperWhitelist)  RETURN p LIMIT 100 
```
