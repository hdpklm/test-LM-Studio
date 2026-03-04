import math
import random

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

def random_matrix(rows, cols, scale=0.02):
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
# Mask
# =========================

def causal_mask(scores):
	size = len(scores)
	for i in range(size):
		for j in range(size):
			if j > i:
				scores[i][j] = -1e9
	return scores

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

# =========================
# Transformer Block
# =========================

def transformer_block(x, params, num_heads):
	attn_out = multi_head_attention(
		x,
		params["Wq"],
		params["Wk"],
		params["Wv"],
		params["Wo"],
		num_heads
	)

	x = layer_norm(add(x, attn_out))

	ff_out = feed_forward(x, params["W1"], params["W2"])
	x = layer_norm(add(x, ff_out))

	return x

# =========================
# Output Projection
# =========================

def output_projection(x, W_out):
	return softmax(matmul(x, W_out))

# =========================
# Model Init
# =========================

def init_model(d_model, d_ff, vocab_size):
	return {
		"embedding": random_matrix(vocab_size, d_model),
		"Wq": random_matrix(d_model, d_model),
		"Wk": random_matrix(d_model, d_model),
		"Wv": random_matrix(d_model, d_model),
		"Wo": random_matrix(d_model, d_model),
		"W1": random_matrix(d_model, d_ff),
		"W2": random_matrix(d_ff, d_model),
		"W_out": random_matrix(d_model, vocab_size),
	}

# =========================
# Forward
# =========================

def forward(tokens, model, num_heads=4):
	x = embedding_lookup(tokens, model["embedding"])
	x = transformer_block(x, model, num_heads)
	return output_projection(x, model["W_out"])

def forward(tokens, model, num_heads=4):
	x = embedding_lookup(tokens, model["embedding"])
	x = transformer_block(x, model, num_heads)

	logits = matmul(x, model["W_out"])
	probs = softmax(logits)

	last_probs = probs[-1]
	next_token = last_probs.index(max(last_probs))

	return next_token

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
				x = transformer_block(x, model, num_heads)
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
	for i in range(len(param)):
		for j in range(len(param[0])):
			param[i][j] -= lr * grad[i][j]

def train_full(model, data, lr=0.001, epochs=10, num_heads=4):

	for epoch in range(epochs):

		total_loss = 0.0

		for tokens in data:

			inputs = tokens[:-1]
			targets = tokens[1:]

			# === Forward ===
			x = embedding_lookup(inputs, model["embedding"])

			Q = matmul(x, model["Wq"])
			K = matmul(x, model["Wk"])
			V = matmul(x, model["Wv"])

			scores = matmul(Q, transpose(K))
			weights = softmax(scores)
			attn_out = matmul(weights, V)

			out = matmul(attn_out, model["Wo"])

			ff_hidden = matmul(out, model["W1"])
			ff_hidden_act = apply_gelu(ff_hidden)
			ff_out = matmul(ff_hidden_act, model["W2"])

			logits = matmul(ff_out, model["W_out"])
			predictions = softmax(logits)

			loss, grad = cross_entropy_with_grad(predictions, targets)
			total_loss += loss

			# === Backward ===
			grad_logits, grad_Wout = linear_backward(ff_out, model["W_out"], grad)

			grad_ff2, grad_W2 = linear_backward(ff_hidden_act, model["W2"], grad_logits)

			gelu_grad = apply_gelu_derivative(ff_hidden)
			grad_gelu = [
				[grad_ff2[i][j] * gelu_grad[i][j] for j in range(len(gelu_grad[0]))]
				for i in range(len(gelu_grad))
			]

			grad_ff1, grad_W1 = linear_backward(out, model["W1"], grad_gelu)

			grad_attn_out, grad_Wo = linear_backward(attn_out, model["Wo"], grad_ff1)

			grad_Q, grad_K, grad_V = attention_backward(Q, K, V, weights, grad_attn_out)

			_, grad_Wq = linear_backward(x, model["Wq"], grad_Q)
			_, grad_Wk = linear_backward(x, model["Wk"], grad_K)
			_, grad_Wv = linear_backward(x, model["Wv"], grad_V)

			# === Update ===
			for name, g in [
				("W_out", grad_Wout),
				("W2", grad_W2),
				("W1", grad_W1),
				("Wo", grad_Wo),
				("Wq", grad_Wq),
				("Wk", grad_Wk),
				("Wv", grad_Wv),
			]:
				sgd_update(model[name], g, lr)

		print("Epoch", epoch+1, "Loss:", total_loss)


# =========================
# Example usage
# =========================

if __name__ == "__main__2":
	d_ff = 32
	d_model = 16
	vocab_size = 32
	model = init_model(d_model, d_ff, vocab_size)

	tokens = [1, 5, 7, 2]		# ejemplo
	output = forward(tokens, model)

	print(output[-1])			# prob del último token


if __name__ == "__main__2":

	d_ff = 32
	d_model = 16
	vocab_size = 32

	model = init_model(d_model, d_ff, vocab_size)

	data = [
		[1, 5, 7, 2, 3],
		[4, 6, 2, 8, 1],
	]

	train(model, data, lr=0.01, epochs=50, batch_size=1)

if __name__ == "__main__":

	d_ff = 32
	d_model = 16
	vocab_size = 32

	model = init_model(d_model, d_ff, vocab_size)

	data = [
		[1, 5, 7, 2, 3],
		[4, 6, 2, 8, 1],
	]

	train_full(model, data, lr=0.01, epochs=50)

	tokens = [1, 5, 7, 2]		# ejemplo
	output = forward(tokens, model)

	print(output)			# prob del último token


