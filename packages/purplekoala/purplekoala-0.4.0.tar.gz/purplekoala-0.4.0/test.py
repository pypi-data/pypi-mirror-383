import math
from scipy.stats import rv_continuous
import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal, localcontext

# import seaborn as sns


class Normal(rv_continuous):
    "Normal"

    def __init__(self, mu, variance, **kwargs):
        super().__init__(**kwargs)
        self.mu = mu
        self.variance = variance

    def _pdf(self, x):
        with localcontext() as ctx:
            ctx.prec = 100  # 100 digits precision
            y = Decimal(0)
            if self.variance <= 0:
                return 0

            """a = 1/np.sqrt(2*np.pi)
        b = 1/np.sqrt(self.variance)
        c = -1.0 * np.pow(np.float128(x-self.mu),2)
        d = 1/2*self.variance

        print("a =",a)
        print("b =",b)
        print("c =",c)
        print("d =",d)"""

            # y = np.float128(a*b*np.float128(np.exp(np.float128(c/d))))

            # left =  (1/(math.sqrt(self.variance)*(math.sqrt(2*math.pi))))
            # right = np.exp(-1*(((x-self.mu)*(x-self.mu))/(2*self.variance)))

            # y = left*right
            # y = (1/(math.sqrt(2*math.pi*self.variance)))*np.exp(-1*(((x-self.mu)**2)/(2*self.variance)))
            y = (1 / math.sqrt(2 * np.pi * self.variance)) * np.exp(
                -(((x - self.mu) ** 2) / (2 * self.variance))
            )

            return y


"""P1 = Normal(name="Normal", mu=0.5, variance=0.3)
    
B1 = P1.rvs(size = 1000)



P2 = Normal(name="Normal", mu=0.5, variance=5.0)
    
B2 = P2.rvs(size = 1000)"""


P3 = Normal(name="Normal", mu=0.5, variance=10.0)

B3 = P3.rvs(size=10000)
