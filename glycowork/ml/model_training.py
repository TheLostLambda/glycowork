import copy
import time
import torch
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, matthews_corrcoef, mean_squared_error

from glycowork.glycan_data.loader import lib
from glycowork.ml.models import SweetNet

class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience."""
    def __init__(self, patience = 7, verbose = False):
        """
        Args:
            patience (int): How long to wait after last time validation loss improved.
                            Default: 7
            verbose (bool): If True, prints a message for each validation loss improvement. 
                            Default: False
        """
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = 0

    def __call__(self, val_loss, model):

        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score:
            self.counter += 1
            print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        '''Saves model when validation loss decrease.'''
        if self.verbose:
            print(f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
        #torch.save(model.state_dict(), 'drive/My Drive/checkpoint.pt')
        self.val_loss_min = val_loss

def train_model(model, dataloaders, criterion, optimizer,
                scheduler, num_epochs = 25, patience = 50,
                mode = 'classification'):
  """
  model -- graph neural network (such as SweetNet) for analyzing glycans\n
  dataloaders -- dictionary of dataloader objects with keys 'train' and 'val'\n
  criterion -- PyTorch loss function\n
  optimizer -- PyTorch optimizer\n
  scheduler -- PyTorch learning rate decay\n
  num_epochs -- number of epochs for training; default: 25\n
  patience -- number of epochs without improvement until early stop; default: 50\n
  mode -- 'classification' or 'regression'; default is binary classification\n

  returns the best model seen during training
  """
  since = time.time()
  early_stopping = EarlyStopping(patience = patience, verbose = True)
  best_model_wts = copy.deepcopy(model.state_dict())
  best_loss = 100.0
  epoch_mcc = 0
  if mode == 'classification':
      best_acc = 0.0
  else:
      best_acc = 100.0
  val_losses = []
  val_acc = []
  
  for epoch in range(num_epochs):
    print('Epoch {}/{}'.format(epoch, num_epochs - 1))
    print('-'*10)
    
    for phase in ['train', 'val']:
      if phase == 'train':
        model.train()
      else:
        model.eval()
        
      running_loss = []
      running_acc = []
      running_mcc = []
      for data in dataloaders[phase]:
        x, y, edge_index, batch = data.x, data.y, data.edge_index, data.batch
        x = x.cuda()
        y = y.cuda()
        edge_index = edge_index.cuda()
        batch = batch.cuda()
        optimizer.zero_grad()

        with torch.set_grad_enabled(phase == 'train'):
          pred = model(x, edge_index, batch)
          loss = criterion(pred, y)

          if phase == 'train':
            loss.backward()
            optimizer.step()
            
        running_loss.append(loss.item())
        if mode == 'classification':
            pred2 = np.argmax(pred.cpu().detach().numpy(), axis = 1)
            running_acc.append(accuracy_score(
                                   y.cpu().detach().numpy().astype(int), pred2))
            running_mcc.append(matthews_corrcoef(y.detach().cpu().numpy(), pred2))
        else:
            running_acc.append(y.cpu().detach().numpy(), pred.cpu().detach().numpy())
        
      epoch_loss = np.mean(running_loss)
      epoch_acc = np.mean(running_acc)
      if mode == 'classification':
          epoch_mcc = np.mean(running_mcc)
      print('{} Loss: {:.4f} Accuracy: {:.4f} MCC: {:.4f}'.format(
          phase, epoch_loss, epoch_acc, epoch_mcc))
      
      if phase == 'val' and epoch_loss <= best_loss:
        best_loss = epoch_loss
        best_model_wts = copy.deepcopy(model.state_dict())
      if mode == 'classification':
          if phase == 'val' and epoch_acc > best_acc:
              best_acc = epoch_acc
      else:
          if phase == 'val' and epoch_acc < best_acc:
              best_acc = epoch_acc
      if phase == 'val':
        val_losses.append(epoch_loss)
        val_acc.append(epoch_acc)
        early_stopping(epoch_loss, model)

      scheduler.step()
        
    if early_stopping.early_stop:
      print("Early stopping")
      break
    print()
    
  time_elapsed = time.time() - since
  print('Training complete in {:.0f}m {:.0f}s'.format(
      time_elapsed // 60, time_elapsed % 60))
  print('Best val loss: {:4f}, best Accuracy score: {:.4f}'.format(best_loss, best_acc))
  model.load_state_dict(best_model_wts)

  ## plot loss & accuracy score over the course of training 
  fig, ax = plt.subplots(nrows = 2, ncols = 1) 
  plt.subplot(2, 1, 1)
  plt.plot(range(epoch+1), val_losses)
  plt.title('Training of SweetNet')
  plt.ylabel('Validation Loss')
  plt.legend(['Validation Loss'],loc = 'best')

  plt.subplot(2, 1, 2)
  plt.plot(range(epoch+1), val_acc)
  plt.ylabel('Validation Accuracy')
  plt.xlabel('Number of Epochs')
  plt.legend(['Validation Accuracy'], loc = 'best')
  return model

def init_weights(model, sparsity = 0.1):
    """initializes linear layers of PyTorch model with a sparse initialization\n
    model -- neural network (such as SweetNet) for analyzing glycans\n
    sparsity -- proportion of sparsity after initialization; default:0.1 / 10%
    """
    if type(model) == torch.nn.Linear:
        torch.nn.init.sparse_(model.weight, sparsity = sparsity)

def prep_model(model_type, num_classes, libr = None):
    """wrapper to instantiate model, initialize it, and put it on the GPU\n
    model_type -- string indicating the type of model\n
    num_classes -- number of unique classes for classification\n
    libr -- sorted list of unique glycoletters observed in the glycans of our dataset\n

    returns PyTorch model object
    """
    if libr is None:
        libr = lib
    if model_type == 'SweetNet':
        model = SweetNet(len(libr), num_classes = num_classes)
        model = model.apply(init_weights)
        model = model.cuda()
    else:
        print("Invalid Model Type")
    return model

def training_setup(model, epochs, lr, lr_decay_length = 0.5, weight_decay = 0.001,
                   mode = 'multiclass'):
    """prepares optimizer, learning rate scheduler, and loss criterion for model training\n
    model -- graph neural network (such as SweetNet) for analyzing glycans\n
    epochs -- number of epochs for training the model\n
    lr -- learning rate\n
    lr_decay_length -- proportion of epochs over which to decay the learning rate;default:0.5\n
    weight_decay -- regularization parameter for the optimizer; default:0.001\n
    mode -- 'multiclass': classification with multiple classes, 'binary':binary classification\n
            'regression': regression; default:'multiclass'\n

    returns optimizer, learning rate scheduler, and loss criterion objects
    """
    lr_decay = np.round(epochs * lr_decay_length)
    optimizer_ft = torch.optim.Adam(model.parameters(), lr = lr,
                                    weight_decay = weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer_ft, lr_decay)
    if mode == 'multiclass':
        criterion = torch.nn.CrossEntropyLoss().cuda()
    elif mode == 'binary':
        criterion = torch.nn.BCEWithLogitsLoss().cuda()
    elif mode == 'regression':
        criterion = torch.nn.MSELoss().cuda()
    else:
        print("Invalid option. Please pass 'multiclass', 'binary', or 'regression'.")
    return optimizer_ft, scheduler, criterion
