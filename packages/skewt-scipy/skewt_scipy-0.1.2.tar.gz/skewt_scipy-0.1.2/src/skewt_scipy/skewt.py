"""
Author         : Jie Li, Innovision IP Ltd and School of Mathematics, Statistics and Actuarial Science, University of Kent.
Date           : 2023-12-24 20:58:11
Last Revision  : 2024-02-28 21:15:18
Last Author : Jieli12
File Path   : /skewt_scipy/src/skewt_scipy/skewt.py
Description    :








Copyright (c) 2023, Jie Li, lijie_12@outlook.com
All Rights Reserved.
"""

# %%
import numpy as np
from scipy import integrate, optimize
from scipy._lib._util import _lazyselect
import scipy._lib.array_api_extra as xpx
from scipy.special import loggamma
from scipy.stats import (
    cauchy,
    chi2,
    f,
    halfcauchy,
    halfnorm,
    norm,
    rv_continuous,
    skewnorm,
    t,
)
from scipy.stats._distn_infrastructure import _ShapeInfo





class skewt_gen(rv_continuous):
    """
    The skew-t distribution
    """

    def _argcheck(self, a, df):
        return True

    def _shape_info(self):
        ia = _ShapeInfo("a", False, (-np.inf, np.inf), (True, True))
        idf = _ShapeInfo("df", False, (0, np.inf), (False, True))
        return [ia, idf]

    def _pdf(self, x, a, df):
        def case1(x, a, df):
            return halfnorm.pdf(x)

        def case2(x, a, df):
            return halfnorm.pdf(-x)

        def case3(x, a, df):
            return skewnorm.pdf(x, a)

        def case4(x, a, df):
            # if df == 1:
            #     return halfcauchy.pdf(x)
            # else:
            #     return xpx.apply_where(
            #         x >= 0,
            #         (x, df),
            #         lambda x_, df_: 2 * t.pdf(x_, df_),
            #         lambda x_, df_: 0.0,
            #     )
            condlist = [df == 1, (df != 1) & (x >= 0), (df != 1) & (x < 0)]
            funclist = [
                lambda x_, df_: halfcauchy.pdf(x_),
                lambda x_, df_: 2 * t.pdf(x_, df_),
                lambda x_, df_: 0.0,
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case4 = np.vectorize(case4, otypes=["float64"])

        def case5(x, a, df):
            # if df == 1:
            #     return halfcauchy.pdf(-x)
            # else:
            #     return xpx.apply_where(
            #         x <= 0,
            #         (x, df),
            #         lambda x_, df_: 2 * t.pdf(-x_, df_),
            #         lambda x_, df_: 0.0,
            #     )
            condlist = [df == 1, (df != 1) & (x <= 0), (df != 1) & (x > 0)]
            funclist = [
                lambda x_, df_: halfcauchy.pdf(-x_),
                lambda x_, df_: 2 * t.pdf(-x_, df_),
                lambda x_, df_: 0.0,
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case5 = np.vectorize(case5, otypes=["float64"])

        def case6(x, a, df):
            return xpx.apply_where(
                df == 1,
                (x, df),
                lambda x_, df_: cauchy.pdf(x_),
                lambda x_, df_: t.pdf(x_, df_),
            )

        def case7_pdf(x, a, df):
            # if df == 1:
            #     return cauchy.pdf(x) * (1 + a * x / np.sqrt(1 + x**2 * (1 + a**2)))
            # else:
            #     return (
            #         2
            #         * t.pdf(x, df)
            #         * t.cdf(a * x * np.sqrt((df + 1) / (x**2 + df)), df + 1)
            #     )
            return xpx.apply_where(
                df == 1,
                (x, a, df),
                lambda x_, a_, df_: cauchy.pdf(x_)
                * (1 + a_ * x_ / np.sqrt(1 + x_**2 * (1 + a_**2))),
                lambda x_, a_, df_: 2
                * t.pdf(x_, df_)
                * t.cdf(a_ * x_ * np.sqrt((df_ + 1) / (x_**2 + df_)), df_ + 1),
            )

        # case7_pdf = np.vectorize(case7_pdf, otypes=["float64"], excluded=["a", "df"])
        return _lazyselect(
            (
                (df == np.inf) & (a == np.inf),
                (df == np.inf) & (a == -np.inf),
                (df == np.inf) & (a != np.inf) & (a != -np.inf),
                (df != np.inf) & (a == np.inf),
                (df != np.inf) & (a == -np.inf),
                (df != np.inf) & (a == 0),
                (df != np.inf) & (a != 0) & (a != np.inf) & (a != -np.inf),
            ),
            (case1, case2, case3, case4, case5, case6, case7_pdf),
            (x, a, df),
        )

    def _logpdf(self, x, a, df):
        def case1(x, a, df):
            return halfnorm.logpdf(x)

        def case2(x, a, df):
            return halfnorm.logpdf(-x)

        def case3(x, a, df):
            return skewnorm.logpdf(x, a)

        def case4(x, a, df):
            # if df == 1:
            #     return halfcauchy.logpdf(x)
            # else:
            #     return xpx.apply_where(
            #         x >= 0,
            #         (x, df),
            #         lambda x_, df_: np.log(2) + t.logpdf(x_, df_),
            #         lambda x_, df_: -np.inf,
            #     )
            condlist = [df == 1, (df != 1) & (x >= 0), (df != 1) & (x < 0)]
            funclist = [
                lambda x_, df_: halfcauchy.logpdf(x_),
                lambda x_, df_: np.log(2) + t.logpdf(x_, df_),
                lambda x_, df_: -np.inf,
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case4 = np.vectorize(case4, otypes=["float64"])

        def case5(x, a, df):
            # if df == 1:
            #     return halfcauchy.logpdf(-x)
            # else:
            #     return xpx.apply_where(
            #         x <= 0,
            #         (x, df),
            #         lambda x_, df_: np.log(2) + t.logpdf(-x_, df_),
            #         lambda x_, df_: -np.inf,
            #     )
            condlist = [df == 1, (df != 1) & (x <= 0), (df != 1) & (x > 0)]
            funclist = [
                lambda x_, df_: halfcauchy.logpdf(-x_),
                lambda x_, df_: np.log(2) + t.logpdf(-x_, df_),
                lambda x_, df_: -np.inf,
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case5 = np.vectorize(case5, otypes=["float64"])

        def case6(x, a, df):
            return xpx.apply_where(
                df == 1,
                (x, df),
                lambda x_, df_: cauchy.logpdf(x_),
                lambda x_, df_: t.logpdf(x_, df_),
            )

        def case7_logpdf(x, a, df):
            # return xpx.apply_where(
            #     df == 1,
            #     (x, a, df),
            #     lambda x_, a_, df_: cauchy.logpdf(x_)
            #     + np.log1p(a_ * x_ / np.sqrt(1 + x_**2 * (1 + a_**2))),
            #     lambda x_, a_, df_: np.log(2)
            #     + t.logpdf(x_, df_)
            #     + t.logcdf(a_ * x_ * np.sqrt((df_ + 1) / (x_**2 + df_)), df_ + 1),
            # )
            def safe_logpdf(x_, a_, df_):
                # Handle edge cases to avoid sqrt warnings
                with np.errstate(invalid='ignore', divide='ignore'):
                    # Compute the argument for sqrt
                    sqrt_arg = (df_ + 1) / (x_**2 + df_)

                    # Check for invalid values
                    valid_mask = np.isfinite(x_) & np.isfinite(sqrt_arg) & (sqrt_arg >= 0)

                    result = np.full_like(x_, -np.inf, dtype=float)

                    if np.any(valid_mask):
                        x_valid = x_[valid_mask] if hasattr(x_, '__len__') else x_
                        a_valid = a_[valid_mask] if hasattr(a_, '__len__') else a_
                        df_valid = df_[valid_mask] if hasattr(df_, '__len__') else df_
                        sqrt_arg_valid = sqrt_arg[valid_mask] if hasattr(sqrt_arg, '__len__') else sqrt_arg

                        result[valid_mask] = (
                            np.log(2)
                            + t.logpdf(x_valid, df_valid)
                            + t.logcdf(a_valid * x_valid * np.sqrt(sqrt_arg_valid), df_valid + 1)
                        )

                    return result

            return xpx.apply_where(
                df == 1,
                (x, a, df),
                lambda x_, a_, df_: cauchy.logpdf(x_)
                + np.log1p(a_ * x_ / np.sqrt(1 + x_**2 * (1 + a_**2))),
                safe_logpdf,
            )

        return _lazyselect(
            (
                (df == np.inf) & (a == np.inf),
                (df == np.inf) & (a == -np.inf),
                (df == np.inf) & (a != np.inf) & (a != -np.inf),
                (df != np.inf) & (a == np.inf),
                (df != np.inf) & (a == -np.inf),
                (df != np.inf) & (a == 0),
                (df != np.inf) & (a != 0) & (a != np.inf) & (a != -np.inf),
            ),
            (case1, case2, case3, case4, case5, case6, case7_logpdf),
            (x, a, df),
        )

    def _cdf(self, x, a, df):
        def case1(x, a, df):
            return halfnorm.cdf(x)

        def case2(x, a, df):
            return 1 - halfnorm.cdf(-x)

        def case3(x, a, df):
            return skewnorm.cdf(x, a)

        def case4(x, a, df):
            # if df == 1:
            #     return xpx.apply_where(
            #         x >= 0, (x), lambda x_: 2 * cauchy.cdf(x_) - 1, lambda x_: 0
            #     )
            # else:
            #     return xpx.apply_where(
            #         x >= 0,
            #         (x, df),
            #         lambda x_, df_: 2 * t.cdf(x_, df_) - 1,
            #         lambda x_, df_: 0,
            #     )
            condlist = [(df == 1) & (x >= 0), (df != 1) & (x >= 0), x < 0]
            funclist = [
                lambda x_, df_: 2 * cauchy.cdf(x_) - 1,
                lambda x_, df_: 2 * t.cdf(x_, df_) - 1,
                lambda x_, df_: 0.0,
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case4 = np.vectorize(case4, otypes=["float64"], excluded=["a", "df"])

        def case5(x, a, df):
            # if df == 1:
            #     return xpx.apply_where(
            #         x >= 0, (x), lambda x_: 1, lambda x_: 2 * (1 - cauchy.cdf(-x_))
            #     )
            # else:
            #     return xpx.apply_where(
            #         x >= 0,
            #         (x, df),
            #         lambda x_, df_: 1,
            #         lambda x_, df_: 2 * (1 - t.cdf(-x_, df_)),
            #     )
            condlist = [x >= 0, (df == 1) & (x < 0), (df != 1) & (x < 0)]
            funclist = [
                lambda x_, df_: 1,
                lambda x_, df_: 2 * (1 - cauchy.cdf(-x_)),
                lambda x_, df_: 2 * (1 - t.cdf(-x_, df_)),
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case5 = np.vectorize(case5, otypes=["float64"], excluded=["a", "df"])

        def case6(x, a, df):
            # if df == 1:
            #     return cauchy.cdf(x)
            # else:
            #     return t.cdf(x, df)
            return xpx.apply_where(
                df == 1,
                (x, df),
                lambda x_, df_: cauchy.cdf(x_),
                lambda x_, df_: t.cdf(x_, df_),
            )

        # case6 = np.vectorize(case6, otypes=["float64"], excluded=["a", "df"])

        def case7_cdf(x, a, df):
            if df == 1:
                # f(x)=1/(pi*(1+x^2))*(1+a*x/sqrt(1+x^2*(1+a^2)))
                # the integrae is 2/pi*atan(x/(1+ax -sqrt(1+x^2*(1+a^2))))
                delta = a / np.sqrt(1 + a**2)
                return (
                    np.arctan(x) / np.pi + np.arccos(delta / np.sqrt(1 + x**2)) / np.pi
                )
            else:
                return integrate.quad(lambda u: self._pdf(u, a, df), -np.inf, x)[0]

            # def f2(x_, a_, df_):
            #     if np.isscalar(x_):
            #         x_ = np.array([x_])
            #     return np.array(
            #         [
            #             integrate.quad(lambda u: self._pdf(u, a_, df_), -np.inf, xi)[0]
            #             for xi in x_
            #         ]
            #     )

            # return xpx.apply_where(
            #     df == 1,
            #     (x, a, df),
            #     lambda x_, a_, df_: np.arctan(x_) / np.pi
            #     + np.arccos(a_ / np.sqrt(1 + a_**2) / np.sqrt(1 + x_**2)) / np.pi,
            #     f2,
            # )

        case7_cdf = np.vectorize(case7_cdf, otypes=["float64"], excluded=["a", "df"])

        return _lazyselect(
            (
                (df == np.inf) & (a == np.inf),
                (df == np.inf) & (a == -np.inf),
                (df == np.inf) & (a != np.inf) & (a != -np.inf),
                (df != np.inf) & (a == np.inf),
                (df != np.inf) & (a == -np.inf),
                (df != np.inf) & (a == 0),
                (df != np.inf) & (a != 0) & (a != np.inf) & (a != -np.inf),
            ),
            (case1, case2, case3, case4, case5, case6, case7_cdf),
            (x, a, df),
        )

    def _logcdf(self, x, a, df):
        def case1(x, a, df):
            return halfnorm.logcdf(x)

        def case2(x, a, df):
            return np.log1p(-halfnorm.cdf(-x))

        def case3(x, a, df):
            return skewnorm.logcdf(x, a)

        def case4(x, a, df):
            # return np.log(self._cdf(x, a, df))

            # if df == 1:
            #     return xpx.apply_where(
            #         x > 0,
            #         (x),
            #         lambda x_: np.log(2 * np.arctan(x) / np.pi),
            #         lambda x_: -np.inf,
            #     )
            # else:
            #     return xpx.apply_where(
            #         x > 0,
            #         (x, df),
            #         lambda x_, df_: np.log(2 * t.cdf(x_, df_) - 1),
            #         lambda x_, df_: -np.inf,
            #     )
            condlist = [(df == 1) & (x > 0), x <= 0, (df != 1) & (x > 0)]
            funclist = [
                lambda x_, df_: np.log(2 * np.arctan(x_) / np.pi),
                lambda x_, df_: -np.inf,
                lambda x_, df_: np.log(2 * t.cdf(x_, df_) - 1),
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case4 = np.vectorize(case4, otypes=["float64"], excluded=["a", "df"])

        def case5(x, a, df):
            # return np.log(self._cdf(x, a, df))
            # if df == 1:
            #     return xpx.apply_where(
            #         x >= 0,
            #         (x),
            #         lambda x_: 0,
            #         lambda x_: np.log(1 - 2 * np.arctan(-x) / np.pi),
            #     )
            # else:
            #     return xpx.apply_where(
            #         x >= 0,
            #         (x, df),
            #         lambda x_, df_: 0,
            #         lambda x_, df_: np.log(2 - 2 * t.cdf(-x_, df_)),
            #     )
            condlist = [x >= 0, (df == 1) & (x < 0), (df != 1) & (x < 0)]
            funclist = [
                lambda x_, df_: 0,
                lambda x_, df_: np.log(1 - 2 * np.arctan(-x_) / np.pi),
                lambda x_, df_: np.log(2 - 2 * t.cdf(-x_, df_)),
            ]
            return _lazyselect(condlist, funclist, [x, df])

        # case5 = np.vectorize(case5, otypes=["float64"], excluded=["a", "df"])

        def case6(x, a, df):
            # if df == 1:
            #     return cauchy.logcdf(x)
            # else:
            #     return t.logcdf(x, df)
            return xpx.apply_where(
                df == 1,
                (x, df),
                lambda x_, df_: cauchy.logcdf(x_),
                lambda x_, df_: t.logcdf(x_, df_),
            )

        # case6 = np.vectorize(case6, otypes=["float64"], excluded=["a", "df"])

        def case7_logcdf(x, a, df):
            if df == 1:
                # f(x)=1/(pi*(1+x^2))*(1+a*x/sqrt(1+x^2*(1+a^2)))
                # the integrae is 2/pi*atan(x/(1+ax -sqrt(1+x^2*(1+a^2))))
                delta = a / np.sqrt(1 + a**2)
                return np.log(
                    np.arctan(x) / np.pi + np.arccos(delta / np.sqrt(1 + x**2)) / np.pi
                )
            else:
                return np.log(
                    integrate.quad(lambda u: self._pdf(u, a, df), -np.inf, x)[0]
                )
            # def f2(x_, a_, df_):
            #     return np.log(
            #         np.array(
            #             [
            #                 integrate.quad(
            #                     lambda u: self._pdf(u, a_, df_), -np.inf, xi
            #                 )[0]
            #                 for xi in x_
            #             ]
            #         )
            #     )

            # return xpx.apply_where(
            #     df == 1,
            #     (x, a, df),
            #     lambda x_, a_, df_: np.log(
            #         np.arctan(x_) / np.pi
            #         + np.arccos(a_ / np.sqrt(1 + a_**2) / np.sqrt(1 + x_**2))
            #         / np.pi
            #     ),
            #     f2,
            # )

        case7_logcdf = np.vectorize(case7_logcdf, otypes=["float64"])

        return _lazyselect(
            (
                (df == np.inf) & (a == np.inf),
                (df == np.inf) & (a == -np.inf),
                (df == np.inf) & (a != np.inf) & (a != -np.inf),
                (df != np.inf) & (a == np.inf),
                (df != np.inf) & (a == -np.inf),
                (df != np.inf) & (a == 0),
                (df != np.inf) & (a != 0) & (a != np.inf) & (a != -np.inf),
            ),
            (case1, case2, case3, case4, case5, case6, case7_logcdf),
            (x, a, df),
        )

    def _ppf(self, q, a, df):
        def case1(q, a, df):
            # return xpx.apply_where(q == 0, (q), lambda q_: 0, lambda q_: halfnorm.ppf(q_))
            return halfnorm.ppf(q)

        def case2(q, a, df):
            return -np.flip(halfnorm.ppf(1 - q))

        def case3(q, a, df):
            return skewnorm.ppf(q, a)

        def case4(q, a, df):
            # if df == 1:
            #     return cauchy.ppf((1 + q) / 2.0)
            # else:
            #     return t.ppf((1 + q) / 2.0, df)
            return xpx.apply_where(
                df == 1,
                (q, df),
                lambda q_, df_: cauchy.ppf((1 + q_) / 2.0),
                lambda q_, df_: t.ppf((1 + q_) / 2.0, df_),
            )

        # case4 = np.vectorize(case4, otypes=["float64"], excluded=["a", "df"])

        def case5(q, a, df):
            # if df == 1:
            #     return cauchy.ppf(q / 2.0)
            # else:
            #     return t.ppf(q / 2.0, df)
            return xpx.apply_where(
                df == 1,
                (q, df),
                lambda q_, df_: cauchy.ppf(q_ / 2.0),
                lambda q_, df_: t.ppf(q_ / 2.0, df_),
            )

        # case5 = np.vectorize(case5, otypes=["float64"], excluded=["a", "df"])

        def case6(q, a, df):
            # if df == 1:
            #     return cauchy.ppf(q)
            # else:
            #     return t.ppf(q, df)
            return xpx.apply_where(
                df == 1,
                (q, df),
                lambda q_, df_: cauchy.ppf(q_),
                lambda q_, df_: t.ppf(q_, df_),
            )

        # case6 = np.vectorize(case6, otypes=["float64"], excluded=["a", "df"])

        def case7_ppf(q, a, df, xtol=1e-8):
            if df == 1:
                delta = a / np.sqrt(1 + a**2)
                u = (q - 0.5) * np.pi
                return np.tan(u) + delta / np.cos(u)
            else:
                if a < 0:
                    q = 1 - q
                # from now on have a>0
                lower = t.ppf(q, df)  # quantiles for a=0
                upper = np.sqrt(f.ppf(q, 1, df))
                if a > 0:
                    return optimize.brentq(
                        lambda x: self._cdf(x, a, df) - q,
                        lower - 1,
                        upper + 1,
                        xtol=xtol,
                    )
                else:
                    return optimize.brentq(
                        lambda x: self._cdf(-x, np.abs(a), df) - q,
                        -upper - 1,
                        -lower + 1,
                        xtol=xtol,
                    )

        case7_ppf = np.vectorize(
            case7_ppf, otypes=["float64"], excluded=["a", "df", "xtol"]
        )
        return _lazyselect(
            (
                (df == np.inf) & (a == np.inf),
                (df == np.inf) & (a == -np.inf),
                (df == np.inf) & (a != np.inf) & (a != -np.inf),
                (df != np.inf) & (a == np.inf),
                (df != np.inf) & (a == -np.inf),
                (df != np.inf) & (a == 0),
                (df != np.inf) & (a != 0) & (a != np.inf) & (a != -np.inf),
            ),
            (case1, case2, case3, case4, case5, case6, case7_ppf),
            (q, a, df),
        )

    def _rvs(self, a, df, size=1, random_state=None):
        if a == np.inf and df == np.inf:
            out = halfnorm.rvs(size=size, random_state=random_state)
        if a == -np.inf and df == np.inf:
            out = -halfnorm.rvs(size=size, random_state=random_state)
        if (df == np.inf) and (a != np.inf) and (a != -np.inf):
            out = skewnorm.rvs(a, size=size, random_state=random_state)
        if (df != np.inf) & (a == np.inf):
            if df == 1:
                out = np.abs(cauchy.rvs(size=size, random_state=random_state))
            else:
                out = np.abs(t.rvs(df, size=size, random_state=random_state))
        if (df != np.inf) & (a == -np.inf):
            if df == 1:
                out = -np.abs(cauchy.rvs(size=size, random_state=random_state))
            else:
                out = -np.abs(t.rvs(df, size=size, random_state=random_state))
        if (df != np.inf) & (a == 0):
            if df == 1:
                out = cauchy.rvs(size=size, random_state=random_state)
            else:
                out = t.rvs(df, size=size, random_state=random_state)
        if (df != np.inf) and (a != np.inf) and (a != -np.inf):
            if df == 1:
                z = skewnorm.rvs(a, loc=0, size=size, random_state=random_state)
                v = np.abs(
                    norm.rvs(loc=0, scale=1, size=size, random_state=random_state)
                )
                out = z / v
            else:
                z = skewnorm.rvs(a, loc=0, size=size, random_state=random_state)
                v = (
                    chi2.rvs(df, loc=0, scale=1, size=size, random_state=random_state)
                    / df
                )
                out = z / np.sqrt(v)
        return out

    def _stats(self, a, df):
        df = xpx.apply_where(df > 66175282, (df), lambda df_: np.inf, lambda df_: df_)
        infinite_df = np.isposinf(df)
        infinite_a = np.isinf(a)
        b_nu = np.repeat(1.0, (len(df),))
        b_nu[~infinite_df] = np.exp(
            0.5 * np.log(df[~infinite_df])
            - 0.5 * np.log(np.pi)
            + loggamma((df[~infinite_df] - 1) / 2)
            - loggamma(df[~infinite_df] / 2)
        )

        delta = np.repeat(np.nan, (len(a),))
        delta[infinite_a] = np.sign(a)[infinite_a]
        delta[~infinite_a] = a[~infinite_a] / np.sqrt(1 + a[~infinite_a] ** 2)

        condlist = (infinite_df, (df > 1) & np.isfinite(df), (df <= 1))
        choicelist = (
            lambda delta, b_nu: np.sqrt(2 / np.pi) * delta,
            lambda delta, b_nu: delta * b_nu,
            lambda delta, b_nu: np.broadcast_to(np.inf, delta.shape),
        )
        mu = _lazyselect(condlist, choicelist, (delta, b_nu), np.nan)

        condlist = (infinite_df, (df > 2) & np.isfinite(df), (df <= 2))
        choicelist = (
            lambda delta, b_nu, df: 1 - 2 * delta**2 / np.pi,
            lambda delta, b_nu, df: df / (df - 2) - (delta * b_nu) ** 2,
            lambda delta, b_nu, df: np.broadcast_to(np.inf, delta.shape),
        )
        mu2 = _lazyselect(condlist, choicelist, (delta, b_nu, df), np.nan)

        condlist = (infinite_df, (df > 3) & np.isfinite(df), (df <= 3))
        choicelist = (
            lambda delta, b_nu, df: (4 - np.pi)
            / 2
            * (delta * np.sqrt(2 / np.pi)) ** 3
            / (1 - 2 * delta**2 / np.pi) ** (3 / 2),
            lambda delta, b_nu, df: b_nu
            * delta
            / (df / (df - 2) - (delta * b_nu) ** 2) ** 1.5
            * (
                df * (3 - delta**2) / (df - 3)
                - 3 * df / (df - 2)
                + 2 * (b_nu * delta) ** 2
            ),
            lambda delta, b_nu, df: np.broadcast_to(np.nan, delta.shape),
        )
        g1 = _lazyselect(condlist, choicelist, (delta, b_nu, df), np.nan)

        condlist = (infinite_df, (df > 4) & np.isfinite(df), (df <= 4))
        choicelist = (
            lambda delta, b_nu, df: 2
            * (np.pi - 3)
            * delta**4
            * 4
            / np.pi**2
            / (1 - 2 * delta**2 / np.pi) ** 2,
            lambda delta, b_nu, df: 1
            / (df / (df - 2) - (delta * b_nu) ** 2) ** 2
            * (
                3 * df**2 / (df - 2) / (df - 4)
                - 4 * (b_nu * delta) ** 2 * df * (3 - delta**2) / (df - 3)
                + 6 * (b_nu * delta) ** 2 * df / (df - 2)
                - 3 * (b_nu * delta) ** 4
            )
            - 3,
            lambda delta, b_nu, df: np.broadcast_to(np.nan, delta.shape),
        )
        g2 = _lazyselect(condlist, choicelist, (delta, b_nu, df), np.nan)
        return mu, mu2, g1, g2


skewt = skewt_gen(name="skewt")

# %%
