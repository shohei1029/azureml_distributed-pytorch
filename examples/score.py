import os
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms

from azureml.core.model import Model

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, 3)
        self.conv3 = nn.Conv2d(64, 128, 3)
        self.fc1 = nn.Linear(128 * 6 * 6, 120)
        self.dropout = nn.Dropout(p=0.2)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128 * 6 * 6)
        x = self.dropout(F.relu(self.fc1(x)))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def init():
    global model
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # For multiple models, it points to the folder containing all deployed models (./azureml-models)
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'cifar_net.pt')
    model = Net()    
    model.load_state_dict(torch.load(model_path,map_location=torch.device('cpu')))
    model.eval()

def run(input_data):
    input_data = torch.tensor(json.loads(input_data)['data'])

    # get prediction
    with torch.no_grad():
        output = model(input_data)
        classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')
        softmax = nn.Softmax(dim=1)
        pred_probs = softmax(output).numpy()[0]

        print("outputです：", output) # output中身確認. n x 10 の行列(リスト入れ子)型tensor

        index = torch.argmax(output, 1) # 元コードで使われていたもの。dim=1がついている
        print("indexです：", index) # 81要素のリスト型tensor

        # index = torch.argmax(output) # dim=1を消したものに置き換えてみた
        # print("indexです：", index) #要素1個。

    result = {"label": classes[index], "probability": str(pred_probs[index])}
    return result
