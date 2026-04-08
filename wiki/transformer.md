# Transformer

> [!TIP]
> The Transformer is a neural network architecture that processes sequential data all at once rather than word-by-word, relying entirely on "attention" to understand the relationships between all parts of the data simultaneously.

## The Core Idea
Historically, sequence tasks (like translation) relied on Recurrent Neural Networks (RNNs) and LSTMs. These models processed sentences token by token, from left to right. This sequential nature created an inescapable bottleneck: they were terribly slow to train (as they couldn't be efficiently parallelized) and struggled to remember context from the beginning of long paragraphs.

The Transformer, introduced by Google researchers in the landmark 2017 paper *"Attention Is All You Need,"* discarded recurrence entirely. Instead, it relies on a "self-attention" mechanism that looks at an entire sequence at once, computing how strongly every word relates to every other word. Because it processes all tokens simultaneously, it massively reduced training times and enabled unprecedented scaling on modern hardware (GPUs/TPUs). This parallelizable nature paved the way for the explosive growth of modern Large Language Models (LLMs) such as GPT, BERT, and Llama.

## How It Works
The original Transformer is composed of an **Encoder** stack and a **Decoder** stack. These stacks are made up of layers containing two primary sub-components: **Multi-Head Self-Attention** and **Position-wise Feed-Forward Networks**.

1. **Positional Encoding:** Because it processes everything in parallel, the architecture natively has no concept of order. It injects mathematically crafted "positional encodings" (often combinations of sines and cosines) into the input embeddings so the network knows the position of each word.
2. **Multi-Head Self-Attention:** Instead of computing a single attention distribution, the model runs multiple self-attention operations in parallel ("heads"). This allows the model to extract complex, multi-faceted relationships (e.g., one head might track pronouns, another might track grammar).
3. **Feed-Forward & Normalization:** The attended representations pass through a two-layer feed-forward network. Crucially, residual (skip) connections and Layer Normalization are applied around every sub-layer to stabilize the gradients during deep training.
4. **The Decoder:** The decoder includes an extra "Cross-Attention" layer to look at the encoder's output. It also explicitly uses *Masked* Self-Attention so it cannot "cheat" by looking at future words during text generation.

![The Transformer Model Architecture](../assets/transformer.png)

## Interview Angle
Transformers are the backbone of modern AI, so standard questions are practically mandatory for NLP engineering roles.

**What gets asked:** "Why are Transformers faster to train than LSTMs?" (Answer: Parallelization). "How does the model know word order?" (Answer: Positional Encodings).

**What trips people up:** Forgetting the LayerNorm or residual connections when describing the architecture block. Another trap is failing to explain the difference between the encoder (bidirectional context) and decoder (autoregressive, masked context).

**A great answer:** An exceptional candidate will discuss the time complexity tradeoff. While recurrent models process in $\mathcal{O}(N)$ sequence steps, self-attention has a computational complexity of $\mathcal{O}(N^2)$ with respect to sequence length. The candidate will explain how this quadratic cost becomes the new bottleneck, smoothly segueing into newer optimizations like FlashAttention or Mixture of Experts (MoE).

---