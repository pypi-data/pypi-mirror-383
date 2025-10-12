import functools
from collections.abc import Sequence

import equinox as eqx
import jax.numpy as jnp
import numpy as np
import warp as wp
from jaxtyping import Array, Float
from warp.jax_experimental import ffi

import liblaf.apple.warp.utils as wp_utils
from liblaf.apple.jax import tree
from liblaf.apple.jax.sim.dirichlet import Dirichlet
from liblaf.apple.jax.sim.model import Model as ModelJax
from liblaf.apple.jax.typing import Scalar, Vector
from liblaf.apple.warp.sim.model import Model as ModelWarp
from liblaf.apple.warp.typing import float_, vec3


def _default_points() -> Float[Array, "0 J"]:
    return jnp.empty((0, 3))


@tree.pytree
class Model:
    points: Float[Array, "p J"] = tree.array(factory=_default_points)
    dirichlet: Dirichlet = tree.field(factory=Dirichlet)
    model_jax: ModelJax = tree.field(factory=ModelJax)
    model_warp: ModelWarp = tree.field(factory=ModelWarp)

    @property
    def n_dirichlet(self) -> int:
        return self.dirichlet.n_dirichlet

    @property
    def n_dofs(self) -> int:
        return self.dirichlet.n_dofs

    @property
    def n_free(self) -> int:
        return self.dirichlet.n_free

    @property
    def n_points(self) -> int:
        return self.points.shape[0]

    @functools.cached_property
    def fun_jax_callable(self) -> ffi.FfiCallable:
        @wp_utils.jax_callable(
            graph_mode=ffi.GraphMode.WARP, output_dims={"output": (1,)}
        )
        def jax_callable(
            u: wp.array(dtype=vec3), output: wp.array(dtype=float_)
        ) -> None:
            output.zero_()
            self.model_warp.fun(u, output)

        return jax_callable

    @functools.cached_property
    def jac_jax_callable(self) -> ffi.FfiCallable:
        @wp_utils.jax_callable(
            graph_mode=ffi.GraphMode.WARP, output_dims={"output": (self.n_points,)}
        )
        def jax_callable(u: wp.array(dtype=vec3), output: wp.array(dtype=vec3)) -> None:
            output.zero_()
            self.model_warp.jac(u, output)

        return jax_callable

    @functools.cached_property
    def hess_diag_jax_callable(self) -> ffi.FfiCallable:
        @wp_utils.jax_callable(
            graph_mode=ffi.GraphMode.WARP, output_dims={"output": (self.n_points,)}
        )
        def jax_callable(u: wp.array(dtype=vec3), output: wp.array(dtype=vec3)) -> None:
            output.zero_()
            self.model_warp.hess_diag(u, output)

        return jax_callable

    @functools.cached_property
    def hess_prod_jax_callable(self) -> ffi.FfiCallable:
        @wp_utils.jax_callable(
            graph_mode=ffi.GraphMode.WARP, output_dims={"output": (self.n_points,)}
        )
        def jax_callable(
            u: wp.array(dtype=vec3),
            p: wp.array(dtype=vec3),
            output: wp.array(dtype=vec3),
        ) -> None:
            output.zero_()
            self.model_warp.hess_prod(u, p, output)

        return jax_callable

    @functools.cached_property
    def hess_quad_jax_callable(self) -> ffi.FfiCallable:
        @wp_utils.jax_callable(
            graph_mode=ffi.GraphMode.WARP, output_dims={"hess_quad": (1,)}
        )
        def jax_callable(
            u: wp.array(dtype=vec3),
            p: wp.array(dtype=vec3),
            output: wp.array(dtype=float_),
        ) -> None:
            output.zero_()
            self.model_warp.hess_quad(u, p, output)

        return jax_callable

    @functools.cached_property
    def fun_and_jac_jax_callable(self) -> ffi.FfiCallable:
        @wp_utils.jax_callable(
            num_outputs=2,
            graph_mode=ffi.GraphMode.WARP,
            output_dims={"fun": (1,), "jac": (self.n_points,)},
        )
        def jax_callable(
            u: wp.array(dtype=vec3),
            fun: wp.array(dtype=float_),
            jac: wp.array(dtype=vec3),
        ) -> None:
            fun.zero_()
            jac.zero_()
            self.model_warp.fun_and_jac(u, fun, jac)

        return jax_callable

    @functools.cached_property
    def jac_and_hess_diag_jax_callable(self) -> ffi.FfiCallable:
        @wp_utils.jax_callable(
            num_outputs=2,
            graph_mode=ffi.GraphMode.WARP,
            output_dims={"jac": (self.n_points,), "hess_diag": (self.n_points,)},
        )
        def jax_callable(
            u: wp.array(dtype=vec3),
            jac: wp.array(dtype=vec3),
            hess_diag: wp.array(dtype=vec3),
        ) -> None:
            jac.zero_()
            hess_diag.zero_()
            self.model_warp.jac_and_hess_diag(u, jac, hess_diag)

        return jax_callable

    @eqx.filter_jit
    def fun(self, u: Vector) -> Scalar:
        u_full: Vector = self.to_full(u)
        outputs_jax: Scalar = self.model_jax.fun(u_full)
        output_wp: Scalar
        (output_wp,) = self.fun_jax_callable(u_full, output_dims={"output": (1,)})
        output_wp = output_wp.squeeze()
        return outputs_jax + output_wp

    @eqx.filter_jit
    def jac(self, u: Vector) -> Vector:
        u_full: Vector = self.to_full(u)
        jac_jax: Vector = self.model_jax.jac(u_full)
        jac_wp: Vector
        (jac_wp,) = self.jac_jax_callable(
            u_full, output_dims={"output": (self.n_points,)}
        )
        jac: Vector = jac_jax + jac_wp
        jac = self.reshape_or_extract_free(jac, u.shape, zero=True)
        return jac

    @eqx.filter_jit
    def hess_diag(self, u: Vector) -> Vector:
        u_full: Vector = self.to_full(u)
        hess_diag_jax: Vector = self.model_jax.hess_diag(u_full)
        hess_diag_wp: Vector
        (hess_diag_wp,) = self.hess_diag_jax_callable(
            u_full, output_dims={"output": (self.n_points,)}
        )
        hess_diag: Vector = hess_diag_jax + hess_diag_wp
        hess_diag = self.reshape_or_extract_free(hess_diag, u.shape, zero=False)
        return hess_diag

    @eqx.filter_jit
    def hess_prod(self, u: Vector, p: Vector) -> Vector:
        u_full: Vector = self.to_full(u)
        p_full: Vector = self.to_full(p, zero=True)
        hess_prod_jax: Vector = self.model_jax.hess_prod(u_full, p_full)
        hess_prod_wp: Vector
        (hess_prod_wp,) = self.hess_prod_jax_callable(
            u_full, p_full, output_dims={"output": (self.n_points,)}
        )
        hess_prod: Vector = hess_prod_jax + hess_prod_wp
        hess_prod = self.reshape_or_extract_free(hess_prod, u.shape, zero=False)
        return hess_prod

    @eqx.filter_jit
    def hess_quad(self, u: Vector, p: Vector) -> Scalar:
        u_full: Vector = self.to_full(u)
        p_full: Vector = self.to_full(p, zero=True)
        hess_quad_jax: Scalar = self.model_jax.hess_quad(u_full, p_full)
        hess_quad_wp: Scalar
        (hess_quad_wp,) = self.hess_quad_jax_callable(
            u_full, p_full, output_dims={"output": (1,)}
        )
        hess_quad_wp = hess_quad_wp.squeeze()
        return hess_quad_jax + hess_quad_wp

    @eqx.filter_jit
    def fun_and_jac(self, u: Vector) -> tuple[Scalar, Vector]:
        u_full: Vector = self.to_full(u)
        fun_jax: Scalar
        jac_jax: Vector
        fun_jax, jac_jax = self.model_jax.fun_and_jac(u_full)
        fun_wp: Scalar
        jac_wp: Vector
        fun_wp, jac_wp = self.fun_and_jac_jax_callable(
            u_full, output_dims={"fun": (1,), "jac": (self.n_points,)}
        )
        fun_wp = fun_wp.squeeze()
        fun: Scalar = fun_jax + fun_wp
        jac: Vector = jac_jax + jac_wp
        jac = self.reshape_or_extract_free(jac, u.shape, zero=True)
        return fun, jac

    @eqx.filter_jit
    def jac_and_hess_diag(self, u: Vector) -> tuple[Vector, Vector]:
        u_full: Vector = self.to_full(u)
        jac_jax: Vector
        hess_diag_jax: Vector
        jac_jax, hess_diag_jax = self.model_jax.jac_and_hess_diag(u_full)
        jac_wp: Vector
        hess_diag_wp: Vector
        jac_wp, hess_diag_wp = self.jac_and_hess_diag_jax_callable(
            u_full, output_dims={"jac": (self.n_points,), "hess_diag": (self.n_points,)}
        )
        jac: Vector = jac_jax + jac_wp
        hess_diag: Vector = hess_diag_jax + hess_diag_wp
        jac = self.reshape_or_extract_free(jac, u.shape, zero=True)
        hess_diag = self.reshape_or_extract_free(hess_diag, u.shape, zero=False)
        return jac, hess_diag

    def mixed_derivative_prod(
        self, u: Vector, p: Vector
    ) -> dict[str, dict[str, Array]]:
        u_full: Vector = self.to_full(u)
        p_full: Vector = self.to_full(p, zero=True)
        outputs: dict[str, dict[str, Array]] = self.model_jax.mixed_derivative_prod(
            u_full, p_full
        )
        outputs_wp: dict[str, dict[str, wp.array]] = (
            self.model_warp.mixed_derivative_prod(
                wp_utils.to_warp(u_full, vec3), wp_utils.to_warp(p_full, vec3)
            )
        )
        for key, value in outputs_wp.items():
            outputs[key] = {k: wp.to_jax(v) for k, v in value.items()}
        return outputs

    def reshape_or_extract_free(
        self, u: Vector, shape: Sequence[int], *, zero: bool = False
    ) -> Vector:
        if u.size == np.prod(shape):
            u = u.reshape(shape)
            if zero:
                u = self.dirichlet.zero(u)
            return u
        return self.dirichlet.get_free(u)

    def to_full(self, u: Vector, *, zero: bool = False) -> Vector:
        if u.size == self.n_dofs:
            return u.reshape(self.points.shape)
        full: Vector = jnp.zeros_like(self.points)
        full = self.dirichlet.set_free(full, u)
        full = self.dirichlet.zero(full) if zero else self.dirichlet.apply(full)
        return full
