# -*- coding: utf-8 -*-
"""QNN_advanced.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jpVTCfLPN0KvVAmnDC6g1WVr-k31MgSU
"""

!pip install qiskit

!pip install matplotlib

!pip install torch

import numpy as np
print(2*np.pi/5)
for j in range(4):
  for m in range(j):
    print(-np.pi/float(j-m))

import numpy as np
import matplotlib.pyplot as plt

import torch
from torch.autograd import Function
from torchvision import datasets, transforms
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F

import qiskit
from qiskit import transpile, assemble
from qiskit.visualization import *

print(np.array([i for i in range(0,5)]))



#setup QuantumCircuit
class QuantumCircuit:
    """ 
    This class provides a simple interface for interaction 
    with the quantum circuit 
    """
    
    def __init__(self, n_qubits, backend, shots):
        # --- Circuit definition ---
        self._circuit = qiskit.QuantumCircuit(n_qubits)
        
        all_qubits = [i for i in range(n_qubits)]
        self.theta = qiskit.circuit.Parameter('theta')
        
        self._circuit.h(all_qubits)
        self._circuit.barrier()
        self._circuit.ry(self.theta, all_qubits)
        
        self._circuit.measure_all()
        # ---------------------------

        self.backend = backend
        self.shots = shots
    
    def run(self, thetas):
        t_qc = transpile(self._circuit,self.backend)
        qobj = assemble(t_qc,shots=self.shots,parameter_binds = [{self.theta: theta} for theta in thetas])
        job = self.backend.run(qobj)
        result = job.result().get_counts()
        
        counts = np.array(list(result.values()))
        states = np.array(list(result.keys())).astype(float)
        
        # Compute probabilities for each state
        probabilities = counts / self.shots
        # Get state expectation
        expectation = np.sum(states * probabilities)
        
        return np.array([expectation])

#setup QuantumCircuit[4,2]
class QuantumCircuits:
    """ 
    This class provides a short interface for interaction 
    with the quantum circuit"""
    
    def __init__(self, n_qubits, backend, shots):
        # --- Circuit definition ---
        self._circuit = qiskit.QuantumCircuit(n_qubits+1,n_qubits+1)
        # For RBS,  all_qubits = 2 ------        
        self._circuit = qiskit.QuantumCircuit(n_qubits) 
        all_qubits = [i for i in range(n_qubits)]
        self.theta = qiskit.circuit.Parameter('theta')
        
        self._circuit.h(all_qubits)
        self._circuit.barrier()
        


        # all_qubits = [n for n in range(1,n_qubits+1)]
        self.theta = qiskit.circuit.Parameter('theta')
        
        self._circuit.x(0)
        self._circuit.h([range(n_qubits+1)])        
        self._circuit.barrier()
        # 
        for i in range(int(n_qubits/2)):
          if i == 0:
            self._circuit.cp(np.pi/n_qubits, i, int(n_qubits/2))
            self._circuit.ry(np.pi/n_qubits, i)
            self._circuit.ry(-np.pi/n_qubits, int(n_qubits/2))
            self._circuit.cp(np.pi/n_qubits, i, int(n_qubits/2)) 
            self._circuit.barrier()
            self._circuit.cp(np.pi/2**i, int(n_qubits/2), int(n_qubits/2+1))
            self._circuit.ry(np.pi/n_qubits, int(n_qubits/2))
            self._circuit.ry(-np.pi/n_qubits, int(n_qubits/2+1))          
            self._circuit.cp(np.pi/2**i, int(n_qubits/2), int(n_qubits/2+1))  
            self._circuit.barrier()           
          else:
            if n_qubits/2-i > 1: 
              self._circuit.cp(np.pi/2**i, int(n_qubits/2-i), int(n_qubits/2-i+1))
              self._circuit.ry(-np.pi/n_qubits, int(n_qubits/2-i))
              self._circuit.ry(np.pi/n_qubits, int(n_qubits/2-i+1))          
              self._circuit.cp(np.pi/2**i, int(n_qubits/2-i), int(n_qubits/2-i+1))
              self._circuit.barrier()
              self._circuit.cp(np.pi/2**i, int(n_qubits/2+i), int(n_qubits/2+i+1))
              self._circuit.ry(np.pi/(n_qubits+1)-np.pi/n_qubits, int(n_qubits/2+i))
              self._circuit.ry(np.pi/n_qubits-np.pi/(n_qubits+1), int(n_qubits/2+i+1))          
              self._circuit.cp(np.pi/2**i, int(n_qubits/2+i), int(n_qubits/2+i+1))
              self._circuit.barrier()
            else:
              for j in range(int(n_qubits/2)):
                if n_qubits/2-i+1+j >= n_qubits/2:
                  self._circuit.cp(np.pi/2**(i-j), int(n_qubits/2-i+j), int(n_qubits/2-i+1+j))
                  self._circuit.ry(-np.pi/n_qubits, int(n_qubits/2-i+j))
                  self._circuit.ry(np.pi/n_qubits, int(n_qubits/2-i+1+j))          
                  self._circuit.cp(np.pi/2**(i-j), int(n_qubits/2-i+j), int(n_qubits/2-i+1+j))
                  self._circuit.h(int(n_qubits/2-i+j))
                  self._circuit.barrier()
                  self._circuit.cp(np.pi/2**(i-j), int(n_qubits/2+i-j), int(n_qubits/2+i+1-j))
                  self._circuit.ry(np.pi/(n_qubits+1)-np.pi/n_qubits, int(n_qubits/2+i-j))
                  self._circuit.ry(np.pi/n_qubits-np.pi/(n_qubits+1), int(n_qubits/2+i+1-j))          
                  self._circuit.cp(np.pi/2**(i-j), int(n_qubits/2+i-j), int(n_qubits/2+i+1-j))
                  self._circuit.h(int(n_qubits/2+i+1-j))
                else:
                  self._circuit.cp(np.pi/n_qubits, 0, int(n_qubits/2))
                  self._circuit.ry(np.pi/n_qubits, 0)
                  self._circuit.ry(-np.pi/n_qubits, int(n_qubits/2))
                  self._circuit.cp(np.pi/n_qubits, 0, int(n_qubits/2)) 
                  self._circuit.h([0,int(n_qubits/2)])
                  self._circuit.barrier()
                  self._circuit.cp(np.pi/2**i, int(n_qubits/2), int(n_qubits/2+1))
                  self._circuit.ry(np.pi/n_qubits, int(n_qubits/2))
                  self._circuit.ry(-np.pi/n_qubits, int(n_qubits/2+1))          
                  self._circuit.cp(np.pi/2**i, int(n_qubits/2), int(n_qubits/2+1))  
                  self._circuit.h(int(n_qubits/2+1))
                  self._circuit.barrier()

#        self._circuit.measure(all_qubits,[n for n in range(n_qubits)])
        self._circuit.measure_all
        # ---------------------------

        self.backend = backend
        self.shots = shots
    
    def run(self, thetas):
        t_qc = transpile(self._circuit,self.backend)
        qobj = assemble(t_qc,shots=self.shots,parameter_binds = [{self.theta: theta} for theta in thetas])
        job = self.backend.run(qobj)
        result = job.result().get_counts()
        
        counts = np.array(list(result.values()))
        states = np.array(list(result.keys())).astype(float)
        
        # Compute probabilities for each state
        probabilities = counts / self.shots
        # Get state expectation
        expectation = np.sum(states * probabilities)
        
        return np.array([expectation])

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import QasmSimulator
from qiskit.visualization import plot_histogram

n_qubits = 4
#circuit = qiskit.QuantumCircuit(n_qubits+1，n_qubits) 
qr = QuantumRegister(n_qubits+1, 'q') 
#cr = ClassicalRegister(n_qubits, 'c')
cr = ClassicalRegister(n_qubits+1, 'c')
print(qr)
print(cr)
circuit = qiskit.QuantumCircuit(qr, cr)    
all_qubits = [i for i in range(1,n_qubits+1)]
theta = qiskit.circuit.Parameter('theta')
circuit.x(0)
#circuit.h([range(n_qubits+1)])        
circuit.barrier()
for i in range(int(n_qubits/2)):
  circuit = qiskit.QuantumCircuit(n_qubits+1)
  all_qubits = [n for n in range(1,n_qubits+1)]
  theta = qiskit.circuit.Parameter('theta')
  circuit.x(0)
  circuit.h([n for n in range(n_qubits+1)])        
  circuit.barrier()
  if i == 0:
    print('i:{}'.format(i))  
    print(n_qubits/2) 
    circuit.cp(np.pi/n_qubits, i, int(n_qubits/2))
    circuit.ry(np.pi/n_qubits, i)
    circuit.ry(-np.pi/n_qubits, int(n_qubits/2))
    circuit.cp(np.pi/n_qubits, i, int(n_qubits/2)) 
    circuit.barrier()           
    circuit.cp(np.pi/2**(i+1), int(n_qubits/2), int(n_qubits/2+1))
    circuit.ry(np.pi/n_qubits, int(n_qubits/2))
    circuit.ry(-np.pi/n_qubits, int(n_qubits/2+1))          
    circuit.cp(np.pi/2**(i+1), int(n_qubits/2), int(n_qubits/2+1)) 
    circuit.barrier()                
  else:
    if n_qubits/2-i > 1: 
      print('i:{}'.format(i))
      print(n_qubits/2-i)
      print(n_qubits/2-i+1)
      print(n_qubits/2+i)
      print(n_qubits/2+i+1)        
      circuit.cp(np.pi/2**(i+1), int(n_qubits/2-i), int(n_qubits/2-i+1))
      circuit.ry(-np.pi/n_qubits, int(n_qubits/2-i))
      circuit.ry(np.pi/n_qubits, int(n_qubits/2-i+1))          
      circuit.cp(np.pi/2**(i+1), int(n_qubits/2-i), int(n_qubits/2-i+1))
      circuit.barrier() 
      circuit.cp(np.pi/2**(i+1), int(n_qubits/2+i), int(n_qubits/2+i+1))
      circuit.ry(np.pi/(n_qubits+1)-np.pi/n_qubits, int(n_qubits/2+i))
      circuit.ry(np.pi/n_qubits-np.pi/(n_qubits+1), int(n_qubits/2+i+1))          
      circuit.cp(np.pi/2**(i+1), int(n_qubits/2+i), int(n_qubits/2+i+1))
      circuit.barrier() 
    else:
      for j in range(int(n_qubits/2)):
        if n_qubits/2-i+1+j >= n_qubits/2:
          print([i,j])
          print(n_qubits/2-i+j)
          print(n_qubits/2-i+1+j)
          print(n_qubits/2+i-j)
          print(n_qubits/2+i+1-j) 
          circuit.cp(np.pi/2**(i-j), int(n_qubits/2-i+j), int(n_qubits/2-i+1+j))
          circuit.ry(-np.pi/n_qubits, int(n_qubits/2-i+j))
          circuit.ry(np.pi/n_qubits, int(n_qubits/2-i+1+j))          
          circuit.cp(np.pi/2**(i-j), int(n_qubits/2-i+j), int(n_qubits/2-i+1+j))
          circuit.h(int(n_qubits/2-i+j))
          circuit.barrier()
          circuit.cp(np.pi/2**(i-j), int(n_qubits/2+i-j), int(n_qubits/2+i+1-j))
          circuit.ry(np.pi/(n_qubits+1)-np.pi/n_qubits, int(n_qubits/2+i-j))
          circuit.ry(np.pi/n_qubits-np.pi/(n_qubits+1), int(n_qubits/2+i+1-j))          
          circuit.cp(np.pi/2**(i-j), int(n_qubits/2+i-j), int(n_qubits/2+i+1-j))
          circuit.h(int(n_qubits/2+i+1-j))
          circuit.barrier() 
        else:
          print([i,j])
          circuit.cp(np.pi/n_qubits, 0, int(n_qubits/2))
          circuit.ry(np.pi/n_qubits, 0)
          circuit.ry(-np.pi/n_qubits, int(n_qubits/2))
          circuit.cp(np.pi/n_qubits, 0, int(n_qubits/2)) 
          circuit.h([0,int(n_qubits/2)])
          circuit.barrier()                  
          circuit.cp(np.pi/2**i, int(n_qubits/2), int(n_qubits/2+1))
          circuit.ry(np.pi/n_qubits, int(n_qubits/2))
          circuit.ry(-np.pi/n_qubits, int(n_qubits/2+1))          
          circuit.cp(np.pi/2**i, int(n_qubits/2), int(n_qubits/2+1))  
          circuit.h(int(n_qubits/2+1))
          circuit.barrier() 
print(qr[1:n_qubits+1])
print(cr[:])
#circuit.measure(qr[1:n_qubits+1], cr[:])
#circuit.measure(np.array([m for m in range(1,n_qubits+1)]), np.array([n for n in range(n_qubits)]))
circuit.measure_all()
#print('Expected value for rotation pi {}'.format(circuit.run([np.pi])[0]))
circuit.draw()

simulator = qiskit.Aer.get_backend('aer_simulator')

qc = QuantumCircuit(4, simulator, 100)
print('Expected value for rotation pi {}'.format(circuit.run([np.pi])[0]))
qc._circuit.draw()

simulator = qiskit.Aer.get_backend('aer_simulator')

circuit = QuantumCircuit(1, simulator, 100)
print('Expected value for rotation pi {}'.format(circuit.run([np.pi])[0]))
circuit._circuit.draw()



class HybridFunction(Function):
    """ Hybrid quantum - classical function definition """
    
    @staticmethod
    def forward(ctx, input, quantum_circuit, shift):
        """ Forward pass computation """
        ctx.shift = shift
        ctx.quantum_circuit = quantum_circuit

        expectation_z = ctx.quantum_circuit.run(input[0].tolist())
        result = torch.tensor([expectation_z])
        ctx.save_for_backward(input, result)

        return result
        
    @staticmethod
    def backward(ctx, grad_output):
        """ Backward pass computation """
        input, expectation_z = ctx.saved_tensors
        input_list = np.array(input.tolist())
        
        shift_right = input_list + np.ones(input_list.shape) * ctx.shift
        shift_left = input_list - np.ones(input_list.shape) * ctx.shift
        
        gradients = []
        for i in range(len(input_list)):
            expectation_right = ctx.quantum_circuit.run(shift_right[i])
            expectation_left  = ctx.quantum_circuit.run(shift_left[i])
            
            gradient = torch.tensor([expectation_right]) - torch.tensor([expectation_left])
            gradients.append(gradient)
        gradients = np.array([gradients]).T
        return torch.tensor([gradients]).float() * grad_output.float(), None, None

class Hybrid(nn.Module):
    """ Hybrid quantum - classical layer definition """
    
    def __init__(self, backend, shots, shift):
        super(Hybrid, self).__init__()
        self.quantum_circuit = QuantumCircuit(1, backend, shots)
        self.shift = shift
        
    def forward(self, input):
        return HybridFunction.apply(input, self.quantum_circuit, self.shift)

# buid hybrid network
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, kernel_size=5)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.dropout = nn.Dropout2d()
        self.fc1 = nn.Linear(256, 64)
        self.fc2 = nn.Linear(64, 1)
        self.hybrid = Hybrid(qiskit.Aer.get_backend('aer_simulator'), 100, np.pi / 2)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = self.dropout(x)
        x = x.view(1, -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = self.hybrid(x)
        return torch.cat((x, 1 - x), -1)



#train
# Concentrating on the first 100 samples
n_samples = 200

X_train = datasets.MNIST(root='./data', train=True, download=True, transform=transforms.Compose([transforms.ToTensor()]))

# Leaving only labels 0 and 1 
idx = np.append(np.where(X_train.targets == 0)[0][:n_samples],np.where(X_train.targets == 1)[0][:n_samples])

X_train.data = X_train.data[idx]
X_train.targets = X_train.targets[idx]

train_loader = torch.utils.data.DataLoader(X_train, batch_size=1, shuffle=True)

#train 
model = Net()
optimizer = optim.Adam(model.parameters(), lr=0.01)
loss_func = nn.NLLLoss()

epochs = 40
loss_list = []

model.train()
for epoch in range(epochs):
    total_loss = []
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        # Forward pass
        output = model(data)
        # Calculating loss
        loss = loss_func(output, target)
        # Backward pass
        loss.backward()
        # Optimize the weights
        optimizer.step()
        
        total_loss.append(loss.item())
    loss_list.append(sum(total_loss)/len(total_loss))
    print(' [{:.0f}%]\t: {:.4f}'.format(
        100. * (epoch + 1) / epochs, -loss_list[-1]))

plt.plot(loss_list)
plt.title('Hybrid ONN Training Convergence')
plt.xlabel('Training Iterations')
plt.ylabel('Neg Log Likelihood Loss')

n_samples_show = 4

data_iter = iter(train_loader)
fig, axes = plt.subplots(nrows=1, ncols=n_samples_show, figsize=(10, 3))

while n_samples_show > 0:
    images, targets = data_iter.__next__()

    axes[n_samples_show - 1].imshow(images[0].numpy().squeeze(), cmap='gray')
    axes[n_samples_show - 1].set_xticks([])
    axes[n_samples_show - 1].set_yticks([])
    axes[n_samples_show - 1].set_title("Labeled: {}".format(targets.item()))
    
    n_samples_show -= 1

#test 
n_samples = 200

X_test = datasets.MNIST(root='./data', train=False, download=True, transform=transforms.Compose([transforms.ToTensor()]))

idx = np.append(np.where(X_test.targets == 0)[0][:n_samples], 
                np.where(X_test.targets == 1)[0][:n_samples])

X_test.data = X_test.data[idx]
X_test.targets = X_test.targets[idx]

test_loader = torch.utils.data.DataLoader(X_test, batch_size=1, shuffle=True)

#test
model.eval()
with torch.no_grad():
    
    correct = 0
    for batch_idx, (data, target) in enumerate(test_loader):
        output = model(data)
        
        pred = output.argmax(dim=1, keepdim=True) 
        correct += pred.eq(target.view_as(pred)).sum().item()
        
        loss = loss_func(output, target)
        total_loss.append(loss.item())
        
    print('Performance on test data:\n\tLoss: {:.4f}\n\tAccuracy: {:.1f}%'.format(
        sum(total_loss) / len(total_loss),
        correct / len(test_loader) * 100)
        )

n_samples_show = 4

data_iter = iter(test_loader)
fig, axes = plt.subplots(nrows=1, ncols=n_samples_show, figsize=(10, 3))

while n_samples_show > 0:
    images, targets = data_iter.__next__()

    axes[n_samples_show - 1].imshow(images[0].numpy().squeeze(), cmap='gray')
    axes[n_samples_show - 1].set_xticks([])
    axes[n_samples_show - 1].set_yticks([])
    axes[n_samples_show - 1].set_title("Labeled: {}".format(targets.item()))
    
    n_samples_show -= 1



n_samples_show = 8
count = 0
fig, axes = plt.subplots(nrows=1, ncols=n_samples_show, figsize=(10, 3))

model.eval()
with torch.no_grad():
    for batch_idx, (data, target) in enumerate(test_loader):
        if count == n_samples_show:
            break
        output = model(data)
        
        pred = output.argmax(dim=1, keepdim=True) 

        axes[count].imshow(data[0].numpy().squeeze(), cmap='gray')

        axes[count].set_xticks([])
        axes[count].set_yticks([])
        axes[count].set_title('Predicted {}'.format(pred.item()))
        
        count += 1

#train 
model = Net()
optimizer = optim.Adam(model.parameters(), lr=0.01)
loss_func = nn.NLLLoss()

epochs = 40
loss_list = []

model.train()
for epoch in range(epochs):
    total_loss = []
    for batch_idx, (data, target) in enumerate(test_loader):
        optimizer.zero_grad()
        # Forward pass
        output = model(data)
        # Calculating loss
        loss = loss_func(output, target)
        # Backward pass
        loss.backward()
        # Optimize the weights
        optimizer.step()
        
        total_loss.append(loss.item())
    loss_list.append(sum(total_loss)/len(total_loss))
    print('Accuracy [{:.0f}%]\tLoss: {:.4f}'.format(
        100. * (epoch + 1) / epochs, -loss_list[-1]))

plt.plot(loss_list)
plt.title('Hybrid NN Training Convergence')
plt.xlabel('Training Iterations')
plt.ylabel('Neg Log Likelihood Loss')