import jax.numpy as jnp
from jaxtyping import Array, Float


def frobenius_norm_square(a: Float[Array, "*b J J"]) -> Float[Array, "*b"]:
    return jnp.sum(jnp.square(a), axis=(-2, -1))
