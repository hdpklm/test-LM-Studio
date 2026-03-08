import math
import random
import json
import os

"""
Dimensiones:
	d_model → dimensión interna del modelo (tamaño del vector por token)
	d_ff → dimensión interna del MLP (normalmente 2x–4x d_model)
	vocab_size → número total de tokens posibles
	num_heads → número de cabezas de atención
	head_dim → d_model / num_heads

Pesos de atención:
	Wq → matriz para generar Queries
	Wk → matriz para generar Keys
	Wv → matriz para generar Values
	Wo → proyección final tras concatenar heads

Dimensiones:
	Wq, Wk, Wv, Wo → (d_model x d_model)

Pesos del MLP
	W1 → primera capa(hidden layer) del feed-forward (d_model → d_ff)
	W2 → segunda capa(output layer) del feed-forward (d_ff → d_model)

Otros pesos
	embedding → matriz (vocab_size x d_model)
	W_out → proyección final (d_model x vocab_size)

Variables intermedias
	Q, K, V → matrices generadas por atención
	scores → QKᵀ / √d_k
	weights → softmax(scores)
	attn_out → salida atención
	ff_out → salida MLP

Dimensiones:
	Q, K, V → (seq_len x d_model)
	scores → (seq_len x seq_len)
	weights → (seq_len x seq_len)
	attn_out → (seq_len x d_model)
	ff_out → (seq_len x d_model)

"""

# =========================
# Utils
# =========================

def zeros(rows, cols):
	return [[0.0 for _ in range(cols)] for _ in range(rows)]

def random_matrix(rows, cols, scale=0.01):
	return [[random.uniform(-scale, scale) for _ in range(cols)] for _ in range(rows)]

def transpose(m):
	return list(map(list, zip(*m)))

def matmul(a, b):
	result = zeros(len(a), len(b[0]))
	for i in range(len(a)):
		for j in range(len(b[0])):
			for k in range(len(b)):
				result[i][j] += a[i][k] * b[k][j]
	return result

def add(a, b):
	return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]

def scalar_divide(m, value):
	return [[x / value for x in row] for row in m]

# =========================
# Activations
# =========================

def gelu(x):
	if x > 10:
		return x
	if x < -10:
		return 0.0
	return 0.5 * x * (1 + math.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * x**3)))

def apply_gelu(m):
	return [[gelu(x) for x in row] for row in m]

def softmax_row(row):
	max_val = max(row)
	exps = [math.exp(x - max_val) for x in row]
	sum_exps = sum(exps)
	return [x / sum_exps for x in exps]

def softmax(m):
	return [softmax_row(row) for row in m]

# =========================
# LayerNorm
# =========================

def mean(row):
	return sum(row) / len(row)

def variance(row, m):
	return sum((x - m) ** 2 for x in row) / len(row)

def layer_norm(x, eps=1e-5):
	output = []
	for row in x:
		m = mean(row)
		v = variance(row, m)
		output.append([(xi - m) / math.sqrt(v + eps) for xi in row])
	return output

# =========================
# Dropout
# =========================

def apply_dropout(x, p=0.1, training=True):
	if not training or p == 0.0:
		return x, None
	
	mask = []
	scale = 1.0 / (1.0 - p)
	output = []
	for row in x:
		out_row = []
		mask_row = []
		for val in row:
			if random.random() < p:
				out_row.append(0.0)
				mask_row.append(0.0)
			else:
				out_row.append(val * scale)
				mask_row.append(scale)
		output.append(out_row)
		mask.append(mask_row)
	return output, mask

def backward_dropout(grad_output, mask):
	if mask is None:
		return grad_output
	return [[g * m for g, m in zip(g_row, m_row)] for g_row, m_row in zip(grad_output, mask)]

# =========================

# Mask
# =========================

def causal_mask(scores):
	size = len(scores)
	for i in range(size):
		for j in range(size):
			if j > i:
				scores[i][j] = -1e9
	return scores

def create_padding_mask(tokens, pad_token=0):
	seq_len = len(tokens)
	mask = zeros(seq_len, seq_len)
	for i in range(seq_len):
		for j in range(seq_len):
			if tokens[j] == pad_token:
				mask[i][j] = -1e9
	return mask

# =========================
# Attention
# =========================

def compute_qkv(x, Wq, Wk, Wv):
	Q = matmul(x, Wq)
	K = matmul(x, Wk)
	V = matmul(x, Wv)
	return Q, K, V

def scaled_dot_product_attention(Q, K, V):
	K_t = transpose(K)
	scores = matmul(Q, K_t)
	scores = scalar_divide(scores, math.sqrt(len(K[0])))
	scores = causal_mask(scores)
	weights = softmax(scores)
	return matmul(weights, V)

# =========================
# Multi Head Attention
# =========================

def split_heads(x, num_heads):
	head_dim = len(x[0]) // num_heads
	heads = []
	for h in range(num_heads):
		start = h * head_dim
		end = start + head_dim
		heads.append([row[start:end] for row in x])
	return heads

def concat_heads(heads):
	seq_len = len(heads[0])
	output = []
	for i in range(seq_len):
		row = []
		for h in heads:
			row.extend(h[i])
		output.append(row)
	return output

def multi_head_attention(x, Wq, Wk, Wv, Wo, num_heads):
	Q, K, V = compute_qkv(x, Wq, Wk, Wv)
	Q_heads = split_heads(Q, num_heads)
	K_heads = split_heads(K, num_heads)
	V_heads = split_heads(V, num_heads)

	heads_output = []
	for i in range(num_heads):
		head = scaled_dot_product_attention(Q_heads[i], K_heads[i], V_heads[i])
		heads_output.append(head)

	concat = concat_heads(heads_output)
	return matmul(concat, Wo)

# =========================
# Feed Forward
# =========================

def feed_forward(x, W1, W2):
	hidden = matmul(x, W1)
	activated = apply_gelu(hidden)
	return matmul(activated, W2)

# =========================
# Embedding
# =========================

def embedding_lookup(tokens, embedding_matrix):
	return [embedding_matrix[token] for token in tokens]

def add_positional_encoding(x):
	seq_len = len(x)
	d_model = len(x[0])
	pe = zeros(seq_len, d_model)
	for pos in range(seq_len):
		for i in range(0, d_model, 2):
			divisor = 10000 ** (i / d_model)
			pe[pos][i] = math.sin(pos / divisor)
			if i + 1 < d_model:
				pe[pos][i+1] = math.cos(pos / divisor)
	return add(x, pe)

# =========================
# Transformer Block
# =========================

def transformer_block(x, params, num_heads, p_drop=0.0, training=False):
	Q = matmul(x, params["Wq"])
	K = matmul(x, params["Wk"])
	V = matmul(x, params["Wv"])

	d_model = len(params["Wq"])
	scores = matmul(Q, transpose(K))
	for i in range(len(scores)):
		for j in range(len(scores[0])):
			scores[i][j] /= math.sqrt(d_model)

	scores = causal_mask(scores)
	weights = softmax(scores)
	
	# Attention Dropout (opcional)
	if training and p_drop > 0.0:
		weights, _ = apply_dropout(weights, p=p_drop, training=training)

	attn_out = matmul(weights, V)
	out = matmul(attn_out, params["Wo"])
	
	out, _ = apply_dropout(out, p=p_drop, training=training)
	out_res = add(x, out)

	ff_hidden = matmul(out_res, params["W1"])
	ff_hidden_act = apply_gelu(ff_hidden)
	ff_out = matmul(ff_hidden_act, params["W2"])

	ff_out, _ = apply_dropout(ff_out, p=p_drop, training=training)
	ff_out_res = add(out_res, ff_out)

	return ff_out_res

# =========================
# Output Projection
# =========================

def output_projection(x, W_out):
	return softmax(matmul(x, W_out))

# =========================
# Model Init
# =========================

def save_model(model, path="micro_weights.json"):
	with open(path, "w") as f:
		json.dump(model, f)

def init_model(d_model, d_ff, vocab_size, load_path=None):
	if load_path and os.path.exists(load_path):
		print(f"Loading weights from {load_path}...")
		with open(load_path, "r") as f:
			model = json.load(f)
			if "history" not in model:
				model["history"] = []
			if "best_loss" not in model:
				model["best_loss"] = float('inf')
			return model

	print("Initializing random weights...")
	return {
		"embedding": random_matrix(vocab_size, d_model),
		"Wq": random_matrix(d_model, d_model),
		"Wk": random_matrix(d_model, d_model),
		"Wv": random_matrix(d_model, d_model),
		"Wo": random_matrix(d_model, d_model),
		"W1": random_matrix(d_model, d_ff),
		"W2": random_matrix(d_ff, d_model),
		"W_out": random_matrix(d_model, vocab_size),
		"history": [],
		"best_loss": float('inf')
	}

def reset_best_loss(model, save=False):
	model["best_loss"] = float('inf')
	if save:
		save_model(model)
	print(" > Record de Loss histórico reseteado a infinito (Preparado para reentrenar sin bloqueo)")

# =========================
# Forward
# =========================

def sample_top_k(probs, top_k=3, top_p=1.0, temperature=1.0):
	scaled_probs = [math.log(p + 1e-9) / temperature for p in probs]
	max_p = max(scaled_probs)
	exps = [math.exp(p - max_p) for p in scaled_probs]
	sum_exps = sum(exps)
	probs = [p / sum_exps for p in exps]

	indexed_probs = list(enumerate(probs))
	indexed_probs.sort(key=lambda item: item[1], reverse=True)
	
	if isinstance(top_k, float) and top_k < 1.0: # Fallback al viejo top_k como top_p
		top_p = top_k
		top_k = len(probs)
	
	valid_probs = []
	cumulative = 0.0
	for idx, p in indexed_probs[:top_k]:
		valid_probs.append((idx, p))
		cumulative += p
		if cumulative >= top_p:
			break
			
	if not valid_probs:
		valid_probs = [indexed_probs[0]]

	sum_valid = sum(p for _, p in valid_probs)
	normalized_valid = [(idx, p / sum_valid) for idx, p in valid_probs]

	r = random.random()
	cumulative = 0.0
	for idx, p in normalized_valid:
		cumulative += p
		if r <= cumulative:
			return idx
	return normalized_valid[-1][0]

def forward(tokens, model, num_heads=4, top_k=3, top_p=1.0, temperature=1.0):
	x = embedding_lookup(tokens, model["embedding"])
	x = add_positional_encoding(x)
	x = transformer_block(x, model, num_heads, training=False)

	logits = matmul(x, model["W_out"])
	probs = softmax(logits)

	last_probs = probs[-1]
	return sample_top_k(last_probs, top_k=top_k, top_p=top_p, temperature=temperature)

def generate(tokens, model, eos_token=256, max_len=50, top_k=3, top_p=1.0, temperature=1.0):
	current_tokens = tokens[:]
	for _ in range(max_len):
		next_token = forward(current_tokens, model, top_k=top_k, top_p=top_p, temperature=temperature)
		current_tokens.append(next_token)
		if next_token == eos_token:
			break
	return current_tokens

# =========================
# Loss
# =========================

def cross_entropy(predictions, targets):
	loss = 0.0
	for i in range(len(targets)):
		loss -= math.log(predictions[i][targets[i]] + 1e-9)
	return loss / len(targets)

def softmax_derivative(predictions, targets):
	grads = []
	for i in range(len(targets)):
		row = predictions[i][:]
		row[targets[i]] -= 1.0
		grads.append(row)
	return grads

def update_W_out(model, x, grad, lr):
	# grad shape: (seq_len × vocab)
	# x shape: (seq_len × d_model)

	d_model = len(x[0])
	vocab_size = len(grad[0])

	for i in range(d_model):
		for j in range(vocab_size):
			delta = 0.0
			for t in range(len(x)):
				delta += x[t][i] * grad[t][j]
			model["W_out"][i][j] -= lr * delta


def train(model, data, lr=0.01, epochs=10, batch_size=1, num_heads=4):

	for epoch in range(epochs):

		total_loss = 0.0

		for batch_start in range(0, len(data), batch_size):

			batch = data[batch_start:batch_start+batch_size]

			for tokens in batch:

				inputs = tokens[:-1]
				targets = tokens[1:]

				# Forward
				x = embedding_lookup(inputs, model["embedding"])
				x = transformer_block(x, model, num_heads, training=True)
				predictions = output_projection(x, model["W_out"])

				# Loss
				loss = cross_entropy(predictions, targets)
				total_loss += loss

				# Backward (solo W_out)
				grad = softmax_derivative(predictions, targets)
				update_W_out(model, x, grad, lr)

		print(f"Epoch {epoch+1}, Loss: {total_loss}")


# =========================
# DERIVADAS
# =========================

def gelu_derivative(x):
	if x > 10:
		return 1.0
	if x < -10:
		return 0.0
	return 0.5 * (1 + math.tanh(math.sqrt(2/math.pi)*(x+0.044715*x**3))) + \
		0.5 * x * (1 - math.tanh(math.sqrt(2/math.pi)*(x+0.044715*x**3))**2) * \
		math.sqrt(2/math.pi) * (1 + 3*0.044715*x**2)

def apply_gelu_derivative(m):
	return [[gelu_derivative(x) for x in row] for row in m]


def linear_forward(x, W):
	return matmul(x, W)

def linear_backward(x, W, grad_output):

	# grad_W = X^T * grad
	x_t = transpose(x)
	grad_W = matmul(x_t, grad_output)

	# grad_input = grad * W^T
	W_t = transpose(W)
	grad_input = matmul(grad_output, W_t)

	return grad_input, grad_W


def cross_entropy_with_grad(pred, targets):

	loss = 0.0
	grad = []

	for i in range(len(targets)):
		row = pred[i][:]
		loss -= math.log(row[targets[i]] + 1e-9)
		row[targets[i]] -= 1.0
		grad.append(row)

	return loss / len(targets), grad


def layer_norm_backward(x, grad_output, eps=1e-5):

	grad_input = []

	for row, grad_row in zip(x, grad_output):

		m = mean(row)
		v = variance(row, m)
		std = math.sqrt(v + eps)

		N = len(row)

		dx = []
		for i in range(N):
			dx.append(grad_row[i] / std)

		grad_input.append(dx)

	return grad_input


# =========================
# Attention backward
# =========================

# Recordemos:
# scores = QKᵀ / √d
# weights = softmax(scores)
# out = weights V

def attention_backward(Q, K, V, weights, grad_output):

	# grad_weights = grad_output * V^T
	V_t = transpose(V)
	grad_weights = matmul(grad_output, V_t)

	# grad_V = weights^T * grad_output
	weights_t = transpose(weights)
	grad_V = matmul(weights_t, grad_output)

	# softmax backward (aprox simplificada)
	grad_scores = grad_weights

	# grad_Q = grad_scores * K
	grad_Q = matmul(grad_scores, K)

	# grad_K = grad_scores^T * Q
	grad_scores_t = transpose(grad_scores)
	grad_K = matmul(grad_scores_t, Q)

	return grad_Q, grad_K, grad_V

def transformer_block_backward(x, params, cache, grad_output, num_heads):

	# unpack cache
	attn_out, ff_hidden = cache

	# === FFN backward ===

	grad_ff2, grad_W2 = linear_backward(ff_hidden, params["W2"], grad_output)

	gelu_grad = apply_gelu_derivative(ff_hidden)

	grad_gelu = [
		[grad_ff2[i][j] * gelu_grad[i][j] for j in range(len(ff_hidden[0]))]
		for i in range(len(ff_hidden))
	]

	grad_ff1, grad_W1 = linear_backward(x, params["W1"], grad_gelu)

	# residual
	grad_attn = add(grad_ff1, grad_output)

	# === Attention backward ===

	grad_attn_input, grad_Wo = linear_backward(attn_out, params["Wo"], grad_attn)

	# Aquí deberíamos dividir heads y aplicar attention_backward por head
	# (simplificado para claridad)
	grad_Q, grad_K, grad_V = attention_backward(
		cache["Q"], cache["K"], cache["V"],
		cache["weights"],
		grad_attn_input
	)

	grad_x_q, grad_Wq = linear_backward(x, params["Wq"], grad_Q)
	grad_x_k, grad_Wk = linear_backward(x, params["Wk"], grad_K)
	grad_x_v, grad_Wv = linear_backward(x, params["Wv"], grad_V)

	grad_x = add(add(grad_x_q, grad_x_k), grad_x_v)

	grads = {
		"W1": grad_W1,
		"W2": grad_W2,
		"Wq": grad_Wq,
		"Wk": grad_Wk,
		"Wv": grad_Wv,
		"Wo": grad_Wo
	}

	return grad_x, grads

def sgd_update(param, grad, lr):
	clip_value = 1.0
	for i in range(len(param)):
		for j in range(len(param[0])):
			g = grad[i][j]
			if g > clip_value:
				g = clip_value
			elif g < -clip_value:
				g = -clip_value
			param[i][j] -= lr * g

def forward_with_cache(inputs, model, p_drop=0.0):
	x_emb = embedding_lookup(inputs, model["embedding"])
	x_pos = add_positional_encoding(x_emb)
	
	x, mask_emb = apply_dropout(x_pos, p=p_drop, training=True)

	Q = matmul(x, model["Wq"])
	K = matmul(x, model["Wk"])
	V = matmul(x, model["Wv"])

	d_model = len(model["Wq"])
	scores = matmul(Q, transpose(K))
	for i in range(len(scores)):
		for j in range(len(scores[0])):
			scores[i][j] /= math.sqrt(d_model)

	scores = causal_mask(scores)
	pad_mask = create_padding_mask(inputs, pad_token=0)
	scores = add(scores, pad_mask)

	weights_raw = softmax(scores)
	
	weights, mask_attn = apply_dropout(weights_raw, p=p_drop, training=True)
	
	attn_out = matmul(weights, V)
	out_raw = matmul(attn_out, model["Wo"])
	
	out, mask_out1 = apply_dropout(out_raw, p=p_drop, training=True)
	out_res = add(x, out)

	ff_hidden = matmul(out_res, model["W1"])
	ff_hidden_act = apply_gelu(ff_hidden)
	ff_out_raw = matmul(ff_hidden_act, model["W2"])
	
	ff_out, mask_out2 = apply_dropout(ff_out_raw, p=p_drop, training=True)
	ff_out_res = add(out_res, ff_out)

	logits = matmul(ff_out_res, model["W_out"])
	predictions = softmax(logits)

	return predictions, {
		"inputs": inputs, "x_emb": x_emb, "x_pos": x_pos, "x": x, "Q": Q, "K": K, "V": V, 
		"weights_raw": weights_raw, "weights": weights, "attn_out": attn_out,
		"out_raw": out_raw, "out": out, "out_res": out_res, 
		"ff_hidden": ff_hidden, "ff_hidden_act": ff_hidden_act, 
		"ff_out_raw": ff_out_raw, "ff_out": ff_out, "ff_out_res": ff_out_res,
		"mask_emb": mask_emb, "mask_attn": mask_attn, "mask_out1": mask_out1, "mask_out2": mask_out2
	}

def backward_pass(model, cache, targets, predictions):
	loss, grad = cross_entropy_with_grad(predictions, targets)

	grad_logits, grad_Wout = linear_backward(cache["ff_out_res"], model["W_out"], grad)
	
	# Pass backwards through dropout 2 y residual 2
	grad_ff_out_res = grad_logits
	
	# Derivar residual branch 2
	grad_out_res_from_res2 = grad_ff_out_res
	grad_ff_out_dropped = grad_ff_out_res
	
	# Revert dropout 2
	grad_ff_out_raw = backward_dropout(grad_ff_out_dropped, cache["mask_out2"])

	grad_ff2, grad_W2 = linear_backward(cache["ff_hidden_act"], model["W2"], grad_ff_out_raw)

	gelu_grad = apply_gelu_derivative(cache["ff_hidden"])
	grad_gelu = [
		[grad_ff2[i][j] * gelu_grad[i][j] for j in range(len(gelu_grad[0]))]
		for i in range(len(gelu_grad))
	]

	grad_ff1, grad_W1 = linear_backward(cache["out_res"], model["W1"], grad_gelu)
	
	# Sumar gradientes en el punto de union del residual 1
	grad_out_res = add(grad_ff1, grad_out_res_from_res2)

	grad_x_from_res1 = grad_out_res
	grad_out_dropped = grad_out_res
	
	# Revert dropout 1
	grad_out_raw = backward_dropout(grad_out_dropped, cache["mask_out1"])

	grad_attn_out, grad_Wo = linear_backward(cache["attn_out"], model["Wo"], grad_out_raw)

	grad_Q, grad_K, grad_V = attention_backward(cache["Q"], cache["K"], cache["V"], cache["weights"], grad_attn_out)
	
	# Aquí en realidad deberíamos hacer backward del dropout de atención:
	# pero attention_backward usa `weights` internamente de forma aproximada al derivar.
    # Dado que es un micro framework educacional, pasamos el dropout en el grad_scores.
	
	d_model = len(model["Wq"])
	for i in range(len(grad_Q)):
		for j in range(len(grad_Q[0])):
			grad_Q[i][j] /= math.sqrt(d_model)
			grad_K[i][j] /= math.sqrt(d_model)

	grad_x_q, grad_Wq = linear_backward(cache["x"], model["Wq"], grad_Q)
	grad_x_k, grad_Wk = linear_backward(cache["x"], model["Wk"], grad_K)
	grad_x_v, grad_Wv = linear_backward(cache["x"], model["Wv"], grad_V)

	# Gradiente sumado que fluye a la base del bloque transformer
	grad_x_dropped = add(add(add(grad_x_q, grad_x_k), grad_x_v), grad_x_from_res1)
	
	# Revert dropout Embedding
	grad_x_pos = backward_dropout(grad_x_dropped, cache["mask_emb"])

	grads = {
		"W_out": grad_Wout, "W2": grad_W2, "W1": grad_W1, "Wo": grad_Wo,
		"Wq": grad_Wq, "Wk": grad_Wk, "Wv": grad_Wv,
		"x": (cache["inputs"], grad_x_pos)
	}
	return loss, grads

def apply_gradients(model, grads, lr, batch_size=1):
	for name, g in grads.items():
		if name == "x":
			if isinstance(g, tuple):
				g = [g]
			for inputs, grad_x in g:
				for t, token_id in enumerate(inputs):
					for j in range(len(grad_x[t])):
						gx = grad_x[t][j] / batch_size
						if gx > 1.0: gx = 1.0
						elif gx < -1.0: gx = -1.0
						model["embedding"][token_id][j] -= lr * gx
		else:
			sgd_update(model[name], g, lr)

def train_full(model, data, lr=0.001, epochs=50, num_heads=4, save_delay=10, dropout=0.0, batch_size=1):
	import copy
	best_loss = model.get("best_loss", float('inf'))
	best_model_copy = None
	wait_counter = 0
	
	epoch_losses = []
	run_best_epoch = 0
	run_best_loss = float('inf')
	
	training_record = {
		"lr": lr,
		"epochs": epochs,
		"dropout": dropout,
		"best_epoch": 0,
		"best_loss": float('inf'),
		"loss_arr": []
	}
	
	if "history" not in model:
		model["history"] = []
	model["history"].append(training_record)

	for epoch in range(epochs):
		total_loss = 0.0
		random.shuffle(data)
		
		batch_grads = None
		current_batch_size = 0

		for tokens in data:
			inputs = tokens[:-1]
			targets = tokens[1:]

			predictions, cache = forward_with_cache(inputs, model, p_drop=dropout)
			loss, grads = backward_pass(model, cache, targets, predictions)
			total_loss += loss

			if batch_grads is None:
				batch_grads = {k: v for k, v in grads.items()}
				batch_grads["x"] = [grads["x"]]
			else:
				for k in grads:
					if k == "x":
						batch_grads["x"].append(grads["x"])
					else:
						batch_grads[k] = add(batch_grads[k], grads[k])
			
			current_batch_size += 1
			
			if current_batch_size == batch_size:
				for k in batch_grads:
					if k != "x":
						batch_grads[k] = scalar_divide(batch_grads[k], batch_size)
				apply_gradients(model, batch_grads, lr, batch_size)
				batch_grads = None
				current_batch_size = 0

		if current_batch_size > 0:
			for k in batch_grads:
				if k != "x":
					batch_grads[k] = scalar_divide(batch_grads[k], current_batch_size)
			apply_gradients(model, batch_grads, lr, current_batch_size)

		print(f"Epoch {epoch+1} Loss: {total_loss}")
		epoch_losses.append(total_loss)
		
		# Actualización en vivo del log por si se guarda prematuramente
		training_record["loss_arr"] = epoch_losses.copy()
		
		if total_loss < best_loss:
			best_loss = total_loss
			run_best_loss = total_loss
			run_best_epoch = epoch + 1
			
			training_record["best_epoch"] = run_best_epoch
			training_record["best_loss"] = run_best_loss
			
			best_model_copy = copy.deepcopy(model)
			print(f" > Nuevo mejor loss en memoria: {best_loss:.4f}")
			if wait_counter == 0:
				wait_counter = save_delay
		
		if wait_counter > 0:
			wait_counter -= 1
			if wait_counter == 0:
				compacted_losses = []
				if len(epoch_losses) <= 100:
					compacted_losses = epoch_losses.copy()
				else:
					chunk_size = len(epoch_losses) / 100.0
					for i in range(100):
						start = int(i * chunk_size)
						end = int((i + 1) * chunk_size)
						chunk = epoch_losses[start:end]
						if chunk:
							compacted_losses.append(sum(chunk) / len(chunk))
				
				best_model_copy["history"][-1]["loss_arr"] = compacted_losses
				save_model(best_model_copy)
				print(f" > Guardado en disco tras esperar {save_delay} epocas (Loss: {best_loss:.4f})")
				
	# Procesar y guardar el historial de entrenamiento final
	compacted_losses = []
	if len(epoch_losses) <= 100:
		compacted_losses = epoch_losses.copy()
	else:
		chunk_size = len(epoch_losses) / 100.0
		for i in range(100):
			start = int(i * chunk_size)
			end = int((i + 1) * chunk_size)
			chunk = epoch_losses[start:end]
			if chunk:
				compacted_losses.append(sum(chunk) / len(chunk))
	
	training_record["loss_arr"] = compacted_losses
	training_record["best_epoch"] = run_best_epoch
	training_record["best_loss"] = run_best_loss
				
	if best_model_copy is not None:
		best_model_copy["best_loss"] = best_loss
		best_model_copy["history"][-1]["loss_arr"] = compacted_losses
		best_model_copy["history"][-1]["best_epoch"] = run_best_epoch
		best_model_copy["history"][-1]["best_loss"] = run_best_loss
		save_model(best_model_copy)
		print(f" > Guardado final en disco al terminar con historial (Loss: {best_loss:.4f})")
	else:
		print(f" > No se superó el record histórico pre-existente ({best_loss:.4f}). Se descartan pesos pero el historial queda temporal en memoria.")
		model["history"].append(training_record)


# =========================
# Example usage
# =========================

if __name__ == "__main__2":
	d_ff = 108
	d_model = 24
	vocab_size = 257
	model = init_model(d_model, d_ff, vocab_size)

	tokens = [1, 5, 7, 2]		# ejemplo
	output = forward(tokens, model)

	print(output)			# prob del último token


if __name__ == "__main__2":

	d_ff = 108
	d_model = 24
	vocab_size = 257

	model = init_model(d_model, d_ff, vocab_size)

	data = [
		[1, 5, 7, 2, 3],
		[4, 6, 2, 8, 1],
	]

	train(model, data, lr=0.01, epochs=50, batch_size=1)

if __name__ == "__main__":

	d_ff = 108
	d_model = 24
	vocab_size = 257

	model = init_model(d_model, d_ff, vocab_size, load_path="micro_weights.json")
	print("Model Best loss: ", model["history"][-1]["best_loss"])

	data = [
		"cuantos años tiene el hassan: hassan tiene 40 años",
		"hola como estas: estoy bien, gracias",
		"donde vive el hassan: hassan vive en Barcelona",
		"donde trabaja el hassan: hassan trabaja en Vilassar de mar",
		"donde nacio el hassan: hassan nacio en Libano",
		"cual es la comida favorita del hassan: la comida favorita del hassan es la pollo",
	]

	# Añadimos el token 256 (EOS) al final de cada frase
	data = [list(s.encode("utf-8")) + [256] for s in data]

	# solo utilizar al añadir mas datos al dataset
	# reset_best_loss(model)
	# train_full(model, data, lr=0.000001, epochs=50, dropout=0.001, batch_size=2)

	prompt = "cuantos años tiene el hassan: "
	prompt = "hola como estas: "
	# prompt = "donde nacio el hassan: "
	tokens = list(prompt.encode("utf-8"))
	
	# Bucle generador
	output_tokens = generate(tokens, model, eos_token=256, max_len=100, top_k=0.1, top_p=0.9, temperature=1.0)

	# Decodificamos omitiendo el prompt inicial
	valid_tokens = [t for t in output_tokens[len(tokens):] if t < 256]
	generated_bytes = bytes(valid_tokens)
	generated_string = generated_bytes.decode("utf-8", errors="replace")
	safe_print = generated_string.encode("ascii", errors="replace").decode("ascii")
	
	# print("Raw Output Tokens:", output_tokens)
	# print("Generación final:", safe_print)
	print(prompt + safe_print)
