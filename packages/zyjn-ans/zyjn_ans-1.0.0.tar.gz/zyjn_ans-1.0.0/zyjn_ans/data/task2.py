import os
import random
import numpy as np
import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from tqdm import tqdm
import cv2
from typing import Tuple
import matplotlib.pyplot as plt

#################################################
class ShapeGenerator:
    def __init__(self, image_size=(64, 64)):
        self.image_size = image_size

    def _create_polygon(self,img,center,radius,sides):
        # <1>
        angles=np.linspeace(0,2*np.pi,sides+1)[:-1]
        points = []
        for angle in angles:
            # <2>
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            points.append([int(x), int(y)])
        pts = np.array(points, np.int32).reshape((-1, 1, 2))
        return cv2.fillPoly(img, [pts], 255)

    def _create_star(self,img,center,size):
        outer_points = []
        inner_points = []
        for i in range(5):
            angle = 2 * np.pi * i / 5 - np.pi / 2
            x = center[0] + size * np.cos(angle)
            y = center[1] + size * np.sin(angle)
            outer_points.append([int(x), int(y)])

            angle += np.pi / 5
            x = center[0] + (size / 2) * np.cos(angle)
            y = center[1] + (size / 2) * np.sin(angle)
            inner_points.append([int(x), int(y)])

        points = []
        for i in range(5):
            points.append(outer_points[i])
            points.append(inner_points[i])

        pts = np.array(points, np.int32).reshape((-1, 1, 2))
        return cv2.fillPoly(img, [pts], 255)

    def create_shape_image(self, shape):
        # <3>
        img = np.zeros((self.image_size[1], self.image_size[0]),dtype=np.uint8)
        center = (self.image_size[0] // 2, self.image_size[1] // 2)
        radius = min(self.image_size) // 4
        try:

            if shape == 'circle':
                # <4>
                img = cv2.circle(img, center, radius, 255, -1)
            elif shape == 'triangle':
                img = self._create_polygon(img, center, radius, 3)
            elif shape == 'rectangle':
                # <5>
                top_left=(center[0]-radius,center[1]-radius)
                bottom_right=(center[0]+radius,center[1]+radius)
                img = cv2.rectangle(img, top_left, bottom_right, 255, -1)
            elif shape == 'pentagon':
                img = self._create_polygon(img, center, radius, 5)
            elif shape == 'hexagon':
                img = self._create_polygon(img, center, radius, 6)
            elif shape == 'star':
                img = self._create_star(img, center, radius)
            else:
                raise ValueError(f"Unsupported shape: {shape}")
        except Exception as e:
            img = cv2.circle(img, center, radius, 255, -1)

        return img
##################################################################
class ShapeDataset(Dataset):
    def __init__(self, root_dir, transform=None, num_samples=300):
        self.root_dir = root_dir
        self.transform = transform
        self.samples = [] # 样本列表
        self.classes = ['circle', 'triangle', 'rectangle', 'pentagon', 'hexagon', 'star']
        self.generator = ShapeGenerator()

        if not os.path.exists(root_dir):
            os.makedirs(root_dir)
            for shape in self.classes:
                shape_dir = os.path.join(root_dir, shape)
                os.makedirs(shape_dir)
                for i in range(num_samples // len(self.classes)):
                    try:
                        img = self.generator.create_shape_image(shape)
                        img_path = os.path.join(shape_dir, f'{i}.png')
                        cv2.imwrite(img_path, img)
                        # <1>
                        self.samples.append((img_path, self.classes.index(shape)))
                    except Exception as e:
                        print("error")
        else:
            for shape in self.classes:
                shape_dir = os.path.join(root_dir, shape)
                if os.path.exists(shape_dir):
                    for filename in os.listdir(shape_dir):
                        self.samples.append((os.path.join(shape_dir, filename), self.classes.index(shape)))
                else:
                    print("目录不存在")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        # <2>
        image = Image.open(img_path).convert("L")
        if self.transform:
            image = self.transform(image)
        return image, label

#############################################################

transform = transforms.Compose([
    transforms.ToTensor(),
    # <1>
    transforms.Normalize((0.5),(0.5))
])

dataset = ShapeDataset(root_dir='./shapes', transform=transform, num_samples=300)
# <2>
dataloader = DataLoader(dataset,shuffle=True,batch_size=64,num_workers=0)

indices = random.sample(range(len(dataset)), 10)
images = []
labels = []

for idx in indices:
    image, label = dataset[idx]
    images.append(image)
    labels.append(label)

# <3>
images = [(img.numpy().squeeze()*0.5+0.5) for img in images]

fig, axes = plt.subplots(2, 5, figsize=(15, 6))
for i, ax in enumerate(axes.flatten()):
    ax.imshow(images[i], cmap='gray')
    ax.set_title(f'Shape: {dataset.classes[labels[i]]}')
    ax.axis('off')

plt.tight_layout()
plt.show()

################################################################
class ComplexCNN(nn.Module):
    def __init__(self):
        super(ComplexCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, 128)
        # <1>
        self.fc3 = nn.Linear(128,len(dataset.classes))
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv3(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 128 * 8 * 8)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x
    
model = ComplexCNN()

criterion = nn.CrossEntropyLoss()
# <2>
optimizer = optim.Adam(model.parameters(),lr=0.001,weight_decay=1e-5)
#######################################################################################
def train(model, dataloader, criterion, optimizer, epochs=6):
    # <1>
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        for i, data in enumerate(tqdm(dataloader, desc=f'Epoch {epoch + 1}/{epochs}')):
            inputs, labels = data
            optimizer.zero_grad()
            outputs=model(inputs)
            loss=criterion(outputs,labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            
            # <3>
            _, predicted = torch.max(outputs.data,1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        print(f'Epoch {epoch + 1}, Loss: {running_loss / (i + 1):.4f}, Accuracy: {accuracy:.2f}%')

train(model, dataloader, criterion, optimizer, epochs=6)
#############################################################################################
def evaluate(model, dataloader):
    model.eval()
    correct = 0 # 样本数量
    total = 0
    # <1>
    with torch.no_grad():
        for data in tqdm(dataloader, desc='Evaluating'):
            images, labels = data
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            # <2>
            correct += (predicted == labels).sum().item()
    print(f'测试准确率: {100 * correct / total:.2f}%')

evaluate(model, dataloader)
######################################################################################################
indices = random.sample(range(len(dataset)), 10)
images = []
labels = []
predictions = []

model.eval()
with torch.no_grad():
    for idx in indices:
        image, label = dataset[idx]
        images.append(image)
        labels.append(label)
        # <1>
        output = model(image.unsqueeze(0))
        _, predicted = torch.max(output.data, 1)
        # <2>
        predictions.append(predicted.item())

images = [img.numpy().transpose((1, 2, 0)) * 0.5 + 0.5 for img in images]

fig, axes = plt.subplots(2, 5, figsize=(15, 6))
for i, ax in enumerate(axes.flatten()):
    ax.imshow(images[i], cmap='gray')
    ax.set_title(f'True: {dataset.classes[labels[i]]}\nPred: {dataset.classes[predictions[i]]}')
    ax.axis('off')

plt.tight_layout()
plt.show()
######################################################################################

