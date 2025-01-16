# uqSim Simulator

## Overview
Implementation of the microservice simulator described in: [uqSim: Scalable and Validated Simulation of Cloud Microservices](https://arxiv.org/abs/1911.02122) with several modifications and extensions for use in the [OPTIMAIX Project](https://github.com/mrichart/optimaix-maps).

## Features

- Scalable simulation of cloud microservices
- Validated against real-world cloud environments
- Extensible architecture for custom modifications
- Integration with the OPTIMAIX Project

## Description

To simulate the execution of an application in the simulator, you first need to define the application and implement the JSON files which describe its behavior.
To set up the simulation, create a new directory for your application inside the `architecture` directory. Within this new directory, include the following JSON files:

### microservice.json / \<ms-name\>.json

Each microservice that composes the application has a corresponding JSON file describing its internal architecture. μqSim models each individual microservice with two orthogonal components: application logic and execution model:

- **Application Logic:** Captures the behavior of a microservice. The basic element is a **stage**, representing an execution phase within the microservice, essentially a queue-consumer pair as defined in queueing theory. Each stage has parameters including processing time and whether it blocks while waiting for a response. μqSim supports processing time expressed using regular distributions or via processing time histograms collected through profiling.

- **Execution Paths:** Multiple application logic stages are assembled to form execution paths, corresponding to a microservice’s different code paths.

### graph.json

Describes the inter-microservice topology and the deployment of each microservice over the infrastructure. It specifies the server on which a microservice is deployed, the resources assigned to each microservice (specific cores), and the execution model (simple or multi-threaded) each microservice is simulated with. The microservice deployment also specifies the size of the connection pool of each microservice, if applicable.

### path.json

Indicates the paths (sequence of microservices) that requests follow across microservices. It specifies the sequence of individual microservices each job needs to go through. Users can also specify multiple inter-microservice paths and the corresponding probability distribution for them.

The basic elements of an inter-microservice path are path nodes, which are connected in a tree structure and serve three roles:

- Specify the microservice, the execution path within the microservice, and the order of traversing individual microservices.
- Express synchronization.
- Encode blocking behavior.

### machines.json

Indicates the name of the server machines and the available resources in the infrastructure. The simulator models one cluster of machines. This file specifies all the machines with the available cores and the network scheduler with the core affinity. 

Network processing is modeled as a separate process in the simulator: each server is coupled with a network processing process as a standalone service, and all microservices deployed on the same server share the process handling interrupts.

### client.json

Specifies the input load pattern.

## Installation

To use the simulator, clone the repository and compile it:

```bash
git clone https://github.com/mrichart/uqsim-power-management-beta.git
cd uqsim-power-management-beta
sh make.sh
```

## Usage

After creating all the JSON files that describe the applications, run the simulation using the following command:

```bash
./microsim ./architecture/<app>/json/ <num_connections> <load_dist> <kilo requests per second>
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or inquiries, please contact the project maintainers at [mrichart@fing.edu.uy](mailto:mrichart@fing.edu.uy).
