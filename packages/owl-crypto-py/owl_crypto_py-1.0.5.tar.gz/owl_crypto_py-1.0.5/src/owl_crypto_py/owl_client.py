import hashlib
import hmac
from typing import Optional, Union
from dataclasses import dataclass

from .owl_common import OwlCommon, ZKP, Point, ZKPVerificationFailure
from .extended_curves import FourQPoint

from messages import (
    AuthFinishRequest,
    AuthInitRequest,
    AuthInitResponse,
    RegistrationRequest,
)


@dataclass
class ClientInitVals:
    username: str
    t: int
    pi: int
    x1: int
    x2: int
    X1: Union[Point, FourQPoint]
    X2: Union[Point, FourQPoint]
    PI1: ZKP
    PI2: ZKP


class UninitialisedClientError(Exception):
    def __init__(self):
        super().__init__("authInit must be run before authFinish")
        self.name = "UninitialisedClientError"


@dataclass
class AuthFinishResult:
    finishRequest: AuthFinishRequest
    key: bytes
    kc: str
    kcTest: str


class OwlClient(OwlCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initValues: Optional[ClientInitVals] = None

    async def register(
        self, username: str, password: str
    ) -> RegistrationRequest:
        # t = H(U||w) mod n
        t = self.modN(await self.H(username + password))
        # pi = H(t) mod n
        pi = self.modN(await self.H(t))
        # T = g * t
        T = self.G.multiply(t)
        return RegistrationRequest(pi, T)

    async def authInit(
        self, username: str, password: str
    ) -> AuthInitRequest:
        # t = H(U||w) mod n
        t = self.modN(await self.H(username + password))
        # pi = H(t) mod n
        pi = self.modN(await self.H(t))
        # x1 = [1, n-1]
        x1 = self.rand(1, self.n - 1)
        # x2 = [1, n-1]
        x2 = self.rand(1, self.n - 1)
        # X1 = G * x1
        X1 = self.G.multiply(x1)
        # X2 = G * x2
        X2 = self.G.multiply(x2)
        # PI1 = ZKP{x1}
        PI1 = await self.createZKP(x1, self.G, X1, username)
        # PI2 = ZKP{x2}
        PI2 = await self.createZKP(x2, self.G, X2, username)
        # keep values for use in authFinish
        self.initValues = ClientInitVals(
            username=username,
            t=t,
            pi=pi,
            x1=x1,
            x2=x2,
            X1=X1,
            X2=X2,
            PI1=PI1,
            PI2=PI2,
        )
        return AuthInitRequest(X1, X2, PI1, PI2)

    async def authFinish(
        self, response: AuthInitResponse
    ) -> Union[AuthFinishResult, ZKPVerificationFailure, UninitialisedClientError]:
        # check authInit has been run
        if not self.initValues:
            return UninitialisedClientError()

        username = self.initValues.username
        t = self.initValues.t
        pi = self.initValues.pi
        x1 = self.initValues.x1
        x2 = self.initValues.x2
        X1 = self.initValues.X1
        X2 = self.initValues.X2
        PI1 = self.initValues.PI1
        PI2 = self.initValues.PI2

        X3 = response.X3
        X4 = response.X4
        PI3 = response.PI3
        PI4 = response.PI4
        beta = response.beta
        PIBeta = response.PIBeta

        # verify ZKPs
        betaG = X1.add(X2).add(X3)
        if (
            not await self.verifyZKP(PI3, self.G, X3, self.serverId)
            or not await self.verifyZKP(PI4, self.G, X4, self.serverId)
            or not await self.verifyZKP(PIBeta, betaG, beta, self.serverId)
        ):
            return ZKPVerificationFailure()

        secret = self.modN(x2 * pi)
        alphaG = X1.add(X3).add(X4)
        # alpha = (X1+X3+X4)*(x2 * pi)
        alpha = alphaG.multiply(secret)
        # PIalpha = ZKP{x2 * pi}
        PIAlpha = await self.createZKP(secret, alphaG, alpha, username)
        # K = (beta - (X4 * (x2 * pi))) * x2
        K = beta.subtract(X4.multiply(secret)).multiply(x2)
        # h = H(K||Transcript)
        h = await self.H(
            K,
            username,
            X1,
            X2,
            PI1.h,
            PI1.r,
            PI2.h,
            PI2.r,
            self.serverId,
            X3,
            X4,
            PI3.h,
            PI3.r,
            beta,
            PIBeta.h,
            PIBeta.r,
            alpha,
            PIAlpha.h,
            PIAlpha.r,
        )
        # r = x1 - (t * h) mod n
        r = self.modN(x1 - t * h)
        # k = H(K) (mutually derived key)
        k = hashlib.sha256(K.toRawBytes()).digest()
        # kc = HMAC(K || "KC" || userId || serverId || X1 || X2 || X3 || X4)
        kc = await self.HMAC(K, username, self.serverId, X1, X2, X3, X4)
        kcTest = await self.HMAC(K, self.serverId, username, X3, X4, X1, X2)

        return AuthFinishResult(
            finishRequest=AuthFinishRequest(alpha, PIAlpha, r),
            key=k,
            kc=kc,
            kcTest=kcTest,
        )