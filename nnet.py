import numpy as np
class neural_net:
	def __init__(self, n_giris, nrons, nrons2, n_cikis):

		self.n_giris = n_giris
		self.nrons = nrons
		self.nrons2 = nrons2
		self.n_cikis = n_cikis
		self.gen_weights()
		self.gen_bias()
		# self.W1 = np.random.randn(self.n_giris, self.nrons)
		# self.W2 = np.random.randn(self.nrons, self.n_cikis)
	def __str__(self):
		return str(self.__dict__)

	def gen_weights(self):
		self.w1	= 2*np.random.rand(self.n_giris,self.nrons)-1
		self.w2	= 2*np.random.rand(self.nrons2,self.nrons)-1
		self.w3 = 2 * np.random.rand(self.n_cikis, self.nrons2) - 1
	def gen_bias(self):
		self.b1	= 2*np.random.rand(1,self.nrons)-1
		self.b2	= 2*np.random.rand(1,self.nrons2)-1
		self.b3 = 2 * np.random.rand(1, self.n_cikis) - 1

	def sigmoid(self,x):
		return 1.0/(1+ np.exp(-x))

	def beyin(self, X):
		X = np.array(X)
		X_norm = (X-X.mean())/X.std()#normalizasyon
		z = (np.dot(X_norm,self.w1)+self.b1)
		z = np.tanh(z)
		a = np.dot(z,self.w2.T)+self.b2
		z1=np.tanh(a)
		a2 = np.dot(z1, self.w3.T) + self.b3
		return self.sigmoid(a2)[0]