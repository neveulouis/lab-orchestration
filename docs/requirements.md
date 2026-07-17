# Requirements — lab-orchestration

## Business requirement

- Build a software to earn a showcase that I am a molecular biologist who builds
  well-structured automation software, shown end-to-end on qPCR.

## User requirements

- As a scientist who runs a workflow (like qPCR), I want to easily orchestrate
  my equipment suite, so that I gain time and decrease variation linked to
  operator effect.
- As a scientist who runs a workflow (like qPCR), I want to automate my data
  analyses, so that I improve my data reproducibility.
- As a workflow author, I want a software that lets me easily wire in a new
  workflow, so that I don't have to write everything from scratch every time.

## Functional requirements

### Engine

**Definition & invocation**

- The system shall allow a workflow to be defined declaratively, without
  touching engine code. (must)
- The system shall validate a workflow definition before execution begins, and
  shall reject an invalid definition with an error identifying what is wrong,
  without executing any step. (must)
- The system shall be invocable from a command line, taking a workflow
  definition as input and running the execution. (must)
- The system shall be runnable from a fresh clone via a single documented
  command, producing a completed run and its analysis output. (must)
- The system shall allow a new workflow to be defined using only one
  workflow-definition file. (could)

**Execution**

- The system shall orchestrate the components of a lab workflow. (must)
- The system shall emit events as steps execute. (must)
- The system shall be able to showcase orchestration across multiple protocol
  steps (sample prep, run). (should)

**Determinism & simulation**

- The system shall be fully executable with simulated instruments, with no
  change to engine or workflow code. (must)
- The system shall provide simulated instruments that generate synthetic
  readings defined by the workflow, not the engine. (must)
- The system shall allow a workflow to declare real durations while the engine
  executes against an injected clock. The simulated clock is the default and
  shall run the workflow in seconds without waiting. Wall-clock is available.
  (must)
- The system shall accept a seed as part of the run configuration and record it
  in the run record, such that the same workflow definition executed with the
  same run configuration produces identical results. (must)

**Failure & traceability**

- The system shall leave every run in exactly one of a defined set of terminal
  states, each with a recorded reason. It shall never silently continue or stop
  a run. (must)
- The system shall log any error, so that failed runs can be traced back. (must)

**Outputs & boundaries**

- The system shall produce a structured, persisted record of what was executed
  during a run. (must)
- The engine shall not know about the data tail. (must)

### qPCR workflow

- The system shall contain a workflow simulating PCR thermal steps. (must)
- The qPCR workflow shall generate synthetic data from a simple parametric curve
  model, not mechanistic reaction kinetics. (must)
- The system shall contain a data suite that automatically performs qPCR
  analyses: (must)
  - Cycle thresholds (must)
  - Quantification (must)
  - Standard curves (must)
  - Melt curves (could)
- The system shall showcase sample-prep automation with liquid handling. (could)

### Data & analyses

- The analysis tail shall be a separate consumer that reads the persisted run
  record after the run terminates. (must)
- The analysis tail shall operate solely on the persisted run record. (must)
- The system shall produce a report presenting the run and its analysis results.
  (must)
- The system shall showcase the data visually using graphs. (should)

## Non-functional requirements

- The system shall run on a laptop from a clone, with no hardware, no network,
  and no external services. (must)
- The system shall be constructed to be reviewed by a technical reviewer and
  provide proof of my coding capacities. (must)

## Won't have

- A second workflow example.
- A GUI.
- A database.
- Any real-hardware execution path.
- Concurrent runs (multiple workflows or instruments at one time).
- An experiment scheduler.
- Modelling of reaction kinetics, instrument physics, or optical response.
- Pausing, resuming, retrying, or cancelling a run in progress.
