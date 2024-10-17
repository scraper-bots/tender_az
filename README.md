### Ticket № 1
**1. Image Classification**
- Task: Classify a dataset of vehicles into different categories.
  - Variant 1: Implement a CNN from scratch.
  - Variant 2: Use a pre-trained model like ResNet and fine-tune it on the vehicle dataset.
  - Variant 3: Explore and compare different data augmentation techniques for image data.

**2. Sentiment Analysis**
- Task: Build a sentiment analysis model to classify movie reviews as positive or negative.
  - Variant 1: Compare the performance of a basic RNN and LSTM.
  - Variant 2: Experiment with word embedding techniques (Word2Vec, GloVe).
  - Variant 3: Train a sentiment analysis model on a different domain such as product reviews.

**3. Image Segmentation**
- Task: Implement an image segmentation model to label objects within medical images.
  - Variant 1: Use the U-Net architecture.
  - Variant 2: Apply DeepLabV3 for semantic segmentation in aerial imagery.
  - Variant 3: Evaluate the impact of different loss functions.

---

### Ticket № 2
**1. Anomaly Detection**
- Task: Build an anomaly detection model for a time series dataset.
  - Variant 1: Apply an Autoencoder-based approach.
  - Variant 2: Use LSTM or GRU for detecting anomalies.
  - Variant 3: Compare models for different types of time series data.

**2. Reinforcement Learning**
- Task: Create an agent that learns to play a game using Deep Q-Networks (DQN).
  - Variant 1: Experiment with different reward structures.
  - Variant 2: Implement a PPO agent.
  - Variant 3: Train an agent to solve a robotics control task.

**3. Generative Adversarial Networks (GANs)**
- Task: Develop a GAN to generate realistic animal images.
  - Variant 1: Try a conditional GAN.
  - Variant 2: Explore WGAN or DCGAN architectures.
  - Variant 3: Train a GAN to generate creative content.

---

### Ticket № 3
**1. Recommendation System**
- Task: Create a music recommendation system using collaborative filtering.
  - Variant 1: Implement matrix factorization-based collaborative filtering.
  - Variant 2: Incorporate neural collaborative filtering.
  - Variant 3: Extend the system to handle multiple content types.

**2. Object Tracking**
- Task: Develop an object tracking system in a video sequence.
  - Variant 1: Use the SORT algorithm.
  - Variant 2: Implement a deep learning-based tracker using Siamese Networks.
  - Variant 3: Evaluate tracking under challenging scenarios.

**3. Speech Recognition**
- Task: Create a speech recognition model.
  - Variant 1: Implement a speech-to-text system using MFCC features and RNN.
  - Variant 2: Explore LAS architecture.
  - Variant 3: Train the model on multilingual data.

---

### Course: Machine Learning - 0255b | Group: E27-24

---

### Ticket № 1
**1. Variance of a Sum**
- Show that the variance of a sum is `var [X + Y] = var [X] + var [Y] + 2cov [X, Y]`.

**2. Conditional Independence**
- Calculate the vector `P(H|e1, e2)` and identify sufficient numbers for this calculation.

**3. Conditional Independence Factorization**
- Prove the alternative definition of conditional independence: `X ⊥ Y | Z`.

---

### Ticket № 2
**1. Beta Updating from Censored Likelihood**
- Compute the posterior `p(θ|X < 3)`.

**2. Posterior Predictive for Dirichlet-Multinomial**
- Calculate probabilities based on the Dirichlet distribution.

**3. Fitting a Naïve Bayes Spam Filter**
- Compute MLEs for spam classification based on the provided vocabulary.

---

### Ticket № 3
**1. Uncorrelated Does Not Imply Independent**
- Show that `ρ(X, Y) = 0` for `X ∼ U(-1, 1)` and `Y = X²`.

**2. MAP Estimation for 1D Gaussians**
- Calculate the MAP estimate `µˆMAP` and show its convergence properties.

**3. Correlation Coefficient Bounds**
- Prove that `−1 ≤ ρ(X, Y) ≤ 1`.

---

This document combines all six tickets for the Deep Learning and Machine Learning courses. Each ticket contains three questions, and each question has three variants for implementation.