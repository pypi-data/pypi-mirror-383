"""
EngiX ML Tools Module
Provides machine learning utilities.
"""

def normalize(data):
    """
    Normalizes data to range [0,1].

    Parameters
    ----------
    data : list
        Input values.

    Returns
    -------
    list
        Normalized data.

    Example
    -------
    >>> normalize([10,20,30])
    [0.0, 0.5, 1.0]
    """
    min_val, max_val = min(data), max(data)
    return [(x-min_val)/(max_val-min_val) for x in data]

def accuracy(y_true, y_pred):
    """
    Computes classification accuracy.

    Example
    -------
    >>> accuracy([0,1,1,0],[0,1,0,0])
    0.75
    """
    correct = sum(yt==yp for yt, yp in zip(y_true, y_pred))
    return correct/len(y_true)

def confusion_matrix(y_true, y_pred, labels):
    """
    Generates confusion matrix.

    Parameters
    ----------
    y_true : list
        True labels.
    y_pred : list
        Predicted labels.
    labels : list
        List of possible labels.

    Returns
    -------
    list of lists
        Confusion matrix.

    Example
    -------
    >>> confusion_matrix([0,1,1,0],[0,1,0,0],[0,1])
    [[2,0],[1,1]]
    """
    matrix = [[0]*len(labels) for _ in labels]
    label_index = {l:i for i,l in enumerate(labels)}
    for yt, yp in zip(y_true, y_pred):
        i = label_index[yt]
        j = label_index[yp]
        matrix[i][j] += 1
    return matrix
