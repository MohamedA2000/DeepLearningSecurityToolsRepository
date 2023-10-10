# DEEP LEARNING SECURITY TOOLS REPOSITORY

Toronto Metropolitan University — Department of Electrical, Computer, and Biomedical Engineering

[2022 COE ENGINEERING DESIGN PROJECT (RSA02)](https://www.ecb.torontomu.ca/capstone/topics/2022/RSA02.html)

[https://rsa02.netlify.app/](https://rsa02.netlify.app/)



## TOPIC CATEGORY

Software Systems

## PREAMBLE

As future technology, such as self-driving cars, are being built using neural networks, the safety of end users is at risk of being compromised by attacks on the neural network. while multiple efforts are being made to generate a set of tools to evaluate privacy and security risks associated with neural networks, there is a lack of aggregator tool for machine learning developers to test the robustness and safety of their deep learning algorithms with multiple tools for benchmarking purposes.

## OBJECTIVE

The objective of this project is to develop an open-source aggregator model focusing on three areas of Deep Neural Network (DNN) security: 1) Privacy, 2) Evasion attacks, and 3) Adversarial Examples.

## PARTIAL SPECIFICATIONS

1. The developed aggregator model must be able to check the resistance of a DNN model against one or more attacks using exiting libraries.
2. The aggregator accepts a model's parameters based on two characteristics of the attack, i.e. (1) Black box or white box and , (2) Privacy, Evasion, and Adversarial Examples.
3. The aggregator asks the user for security test parameters such as the number of epochs, number of folds, number of layers and other architectural questions.
4. The aggregator, calls the relevant libraries (that have already been collected) and runs the model-at-the-test for the given parameters.
5. The results are reported in tables and static and dynamic graphs in a user-friendly manner.

## SUGGESTED APPROACH

- The first step is to study for available Trustworthy ML libraries. for example: NIST Dioptra Project, Machine Learning Privacy Meter, CleverHans Repository, and Fool Box.
- Then to create a framework which accepts neural networks from Keras, one of the industry standard machine learning frameworks built on top of TensorFlow.
- The Framework should have a user-friendly and easy-to-learn interface to define DNN pipeline and set all parameters. The parameters need to be all stored, and the parameters of each run should be fully logged.
- Depending on the parameters, the framework selects the libraries from the repository, checks the model against the selected attack and generates the results.
- The Framework then communicates the results in three forms, Tables, static graphs and dynamic graphs using Python Libraries (eg., Tensorboard for dynamic graphs).



- Design user interface (UI) module
- Implement front-end of "what-if" scenarios working with Student B and C
- Prototyping the system UI
- Running usability test
- Integrate with back-end module
