# 🚀 Transformer Architecture – Interactive Learning Platform

<p align="center">
  <b>An interactive platform to deeply understand the internal mechanics of the Transformer model.</b>
</p>

<p align="center">
  🌐 <a href="https://transformer-lime.vercel.app/">Live Demo</a>
</p>

---

## 📖 Overview

This project is a browser-based interactive learning platform designed to explore the Transformer architecture from first principles.

Instead of only reading theory, this platform converts mathematical equations into working logic and visual explanations. It demonstrates how attention mechanisms operate internally and how encoder–decoder blocks interact within the model.

---

## 🧠 Concepts Implemented

- Token Embeddings  
- Positional Encoding (Sine–Cosine formulation)  
- Scaled Dot-Product Attention  
- Multi-Head Attention  
- Masked Self-Attention  
- Residual Connections  
- Layer Normalization  
- Position-wise Feed Forward Network  
- Encoder–Decoder Stack Architecture  

---

## 🔬 Core Attention Formula

Scaled Dot-Product Attention:

Attention(Q, K, V) = softmax((QKᵀ) / √dₖ) V

Implementation includes:

- Linear projections for Query, Key, and Value  
- Dot-product similarity computation  
- Scaling by √dₖ for variance normalization  
- Softmax normalization  
- Weighted aggregation with V  
- Multi-head splitting and concatenation  

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML5, CSS3, JavaScript |
| Architecture Logic | Custom Implementation |
| Deployment | Vercel |

This project runs fully on the client side.

---

## 🌐 Deployment

Live Application:
https://transformer-lime.vercel.app/

Hosted using Vercel with:

- Automatic GitHub deployment  
- HTTPS enabled  
- Global CDN  
- Fast static serving  
