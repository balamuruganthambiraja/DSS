import torch
import math
import unittest

from .mathHelper import normalize


def rotationMatrixX(alpha):
    tc = torch.cos(alpha)
    ts = torch.sin(alpha)
    R = torch.eye(3, device=alpha.device)
    R[1, 1] = tc
    R[2, 2] = tc
    R[1, 2] = -ts
    R[2, 1] = ts
    return R


def rotationMatrixY(alpha):
    tc = torch.cos(alpha)
    ts = torch.sin(alpha)
    R = torch.eye(3, device=alpha.device)
    R[0, 0] = tc
    R[2, 2] = tc
    R[2, 0] = -ts
    R[0, 2] = ts
    return R


def rotationMatrixZ(alpha):
    tc = torch.cos(alpha)
    ts = torch.sin(alpha)
    R = torch.eye(3, device=alpha.device)
    R[0, 0] = tc
    R[1, 1] = tc
    R[0, 1] = -ts
    R[1, 0] = ts
    return R


def rotationMatrix(alpha, beta, gamma):
    return rotationMatrixX(alpha).mm(rotationMatrixY(beta).mm(rotationMatrixZ(gamma)))


def convertWorldToCameraTransform(Rw, C):
    """ 
    Takes a camera transformation in world space and returns the camera transformation in camera space to be used as extrinsic parameters 
    Rw (B, 3, 3)
    C  (B, 3)
    """
    Rc = Rw.transpose(1, 2)
    t = -Rc.matmul(C.unsqueeze(-1)).squeeze(-1)
    return (Rc, t)


def batchAffineMatrix(R, t, scale):
    """
    affine transformation with uniform scaling->rotation->tranlation
    """
    if R.dim() == 2:
        T = torch.eye(4, dtype=R.dtype, device=R.device)
        T[:3, :3] = R*scale
        T[:3, -1] = t
    else:
        B, _, _ = R.shape
        T = torch.eye(4, dtype=R.dtype, device=R.device)
        T = T.unsqueeze(0).expand(B, -1, -1)
        T[:, :3, :3] = R*scale
        T[:, :3, -1] = t
    return T


def batchLookAt(fromP, toP, upP):
    """
    construct rotation and translation using from, forward, upward vectors
    fromP batches of (3,) vectors
    toP batches of (3,) vectors
    upP batches of (3,) vectors
    """
    # change (..., 3) to (..., 3, 3)
    shapeP = list(fromP.shape)
    shapeP.append(3)
    translation = fromP
    fromP = fromP.view(-1, 3)
    toP = toP.view(-1, 3)
    upP = upP.view(-1, 3)
    b, _ = fromP.shape
    forward = normalize(toP - fromP, dim=-1)
    right = normalize(forward.cross(upP), dim=-1)
    upP = normalize(right.cross(forward), dim=-1)
    rotation = torch.empty([b, 3, 3], device=fromP.device)
    rotation[:, :, 0] = right
    rotation[:, :, 1] = upP
    rotation[:, :, 2] = forward
    rotation = rotation.view(*shapeP)
    return rotation, translation


def lookAt(fromP, toP, upP):
    forward = normalize(toP - fromP)
    right = normalize(forward.cross(upP))
    upP = right.cross(forward)
    rotation = torch.empty([3, 3], device=fromP.device)
    rotation[:, 0] = right
    rotation[:, 1] = upP
    rotation[:, 2] = forward
    translation = fromP
    return (rotation, translation)


if __name__ == '__main__':
    unittest.main()
