# uqSim Simulator

## Overview
Implementation of the microservice simulator described in: [uqSim: Scalable and Validated Simulation of Cloud Microservices](https://arxiv.org/abs/1911.02122) with several modifications and extensions to be used in the [OPTIMAIX Project](https://github.com/mrichart/optimaix-maps).

## Features

- Scalable simulation of cloud microservices
- Validated against real-world cloud environments
- Extensible architecture for custom modifications
- Integration with the OPTIMAIX Project

## Description

To simulate the execution of an application in the simulator, first you need to define the application and implement the json fies which describe its behaviour.

**microservice.json / <ms-name>.json**

There is one json for each microservice which compose the application which describes the internal architecture of the microservice.
μqSim models each individual microservice with two orthogonal components: **application logic and execution model:**

- The application logic captures the behavior of a microservice. The basic element of the application logic is a **stage**, which represents an execution phase within the microservice, and is essentially a queue-consumer pair, as defined in queueing theory. Each stage has a set of parameters which include the processing time and if it blocks while waiting for a response. μqSim supports processing time expressed using regular distributions or via processing time histograms collected through profiling. 

- Multiple application logic stages are assembled to form **execution paths**, corresponding to a microservice’s different code paths.

The model of a microservice also includes a **state machine that specifies the probability** that a microservice follows different execution paths.

**graph.json** 

Describes the inter-microservice topology as well as the deployment of each microservice over the infrastructure. It **specifies the server on which a microservice is deployed** – if specified, **the resources assigned to each microservice (which specific cores)**, and the **execution model (simple or multi-threaded)** each microservice is simulated with. The microservice deployment also specifies the **size of the connection pool of each microservice**, if applicable.

**path.json** 

In this file is indicated the paths (sequence of microservices) that requests follow across microservices. In particular, it specifies the sequence of individual microservices each job needs to go through. 

**El path es de ida y vuelta**

Users can also specify **multiple inter-microservice paths**, and the corresponding **probability distribution** for them.

The basic elements of an inter-microservice path are path nodes, which are connected in a tree structure and serve three roles:

- Specify the microservice, the execution path within the microservice, and the order of traversing individual microservices.
- Express synchronization
- Encode blocking behavior

**machines.json** 

Indicates the name of the server machines and the available resources in the infrastructure. The simulator only models one cluster of machines and the latency is not specified in this file.

In this file you specify all the machines with the avaiable cores and the network scheduler with the core affinity.

This excludes network processing, which is modeled as a separate process in the simulator: each server is coupled with a network processing process as a standalone service, and all microservices deployed on the same server share the processed handling interrupts.

**client.json**

Input load pattern.

## Installation

To use the simulator, clone the repository and compile it:

```bash
git clone https://github.com/mrichart/uqsim-power-management-beta.git
cd uqsim-power-management-beta
sh make.sh
```

## Usage

After all the json which describe the applications are created, the simulation is ran using the following command:

```bash
./microsim ./architecture/<app>/json/ <num_connections> <load_dist> <kilo requests per second>
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or inquiries, please contact the project maintainers at [mrichart@fing.edu.uy](mailto:mrichart@fing.edu.uy).