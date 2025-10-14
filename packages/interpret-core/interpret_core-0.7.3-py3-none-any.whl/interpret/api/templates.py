# Copyright (c) 2023 The InterpretML Contributors
# Distributed under the MIT software license

import interpret.api.base


class FeatureValueExplanation(interpret.api.base.ExplanationMixin):
    """Handles explanations that can be visualized as horizontal bar graphs.
    Usually these are feature-value pairs being represented.
    """

    explanation_type = None

    def __init__(
        self,
        explanation_type,
        internal_obj,
        feature_names=None,
        feature_types=None,
        name=None,
        selector=None,
    ):
        """Initializes class.

        Args:
            explanation_type:  Type of explanation.
            internal_obj: A jsonable object that backs the explanation.
            feature_names: List of feature names.
            feature_types: List of feature types.
            name: User-defined name of explanation.
            selector: A dataframe whose indices correspond to explanation entries.
        """
        self.explanation_type = explanation_type
        self._internal_obj = internal_obj
        self.feature_names = feature_names
        self.feature_types = feature_types
        self.name = name
        self.selector = selector

    def data(self, key=None):
        """Provides specific explanation data.

        Args:
            key: A number/string that references a specific data item.

        Returns:
            A serializable dictionary.
        """
        # NOTE: When a non-default provider is used, it's represented as ("provider", key).
        if isinstance(key, tuple) and len(key) == 2:
            _, key = key

        # NOTE: Currently returns full internal object, open to change.
        if key == -1:
            return self._internal_obj

        if key is None:
            return self._internal_obj["overall"]

        if self._internal_obj["specific"] is None:  # pragma: no cover
            return None
        return self._internal_obj["specific"][key]

    def visualize(self, key=None, title=None):
        """Provides interactive visualizations.

        Args:
            key: Either a scalar or list
                that indexes the internal object for sub-plotting.
                If an overall visualization is requested, pass None.

        Returns:
            A Plotly figure.
        """
        from ..visual.plot import (
            get_explanation_index,
            get_sort_indexes,
            is_multiclass_local_data_dict,
            mli_plot_horizontal_bar,
            mli_sort_take,
            plot_bar,
            plot_horizontal_bar,
            plot_line,
            plot_pairwise_heatmap,
            sort_take,
        )

        data_dict = self.data(key)
        if data_dict is None:  # pragma: no cover
            return None

        # Handle overall graphs
        if key is None:
            data_dict = sort_take(
                data_dict, sort_fn=lambda x: -abs(x), top_n=15, reverse_results=True
            )
            return plot_horizontal_bar(data_dict)

        # Handle local instance graphs
        if self.explanation_type == "local":
            if isinstance(key, tuple) and len(key) == 2:
                provider, key = key
                # TODO: MLI should handle multiclass at a future date.
                if provider == "mli" and "mli" in self.data(-1):
                    explanation_list = self.data(-1)["mli"]
                    explanation_index = get_explanation_index(
                        explanation_list, "local_feature_importance"
                    )
                    local_explanation = explanation_list[explanation_index]["value"]
                    scores = local_explanation["scores"]
                    perf = local_explanation["perf"]
                    sort_indexes = get_sort_indexes(
                        scores[key], sort_fn=lambda x: -abs(x), top_n=15
                    )
                    sorted_scores = mli_sort_take(
                        scores[key], sort_indexes, reverse_results=True
                    )
                    sorted_names = mli_sort_take(
                        self.feature_names, sort_indexes, reverse_results=True
                    )
                    instances = explanation_list[1]["value"]["dataset_x"]
                    return mli_plot_horizontal_bar(
                        sorted_scores,
                        sorted_names,
                        values=instances[key],
                        perf=perf[key],
                    )
                # pragma: no cover
                msg = f"Visual provider {provider} not supported"
                raise RuntimeError(msg)
            is_multiclass = is_multiclass_local_data_dict(data_dict)
            if is_multiclass:
                # Sort by predicted class' abs feature values
                pred_idx = data_dict["perf"]["predicted"]

                def sort_fn(x):
                    return -abs(x[pred_idx])
            else:
                # Sort by abs feature values
                def sort_fn(x):
                    return -abs(x)

            data_dict = sort_take(
                data_dict, sort_fn=sort_fn, top_n=15, reverse_results=True
            )
            return plot_horizontal_bar(data_dict, multiclass=is_multiclass)

        # Handle global feature graphs
        feature_type = self.feature_types[key]
        if title is None:
            title = self.feature_names[key]
        if feature_type == "continuous":
            return plot_line(data_dict, title=title)
        if feature_type in ("nominal", "ordinal"):
            return plot_bar(data_dict, title=title)
        if feature_type == "interaction":
            # TODO: Generalize this out.
            xtitle = self.feature_names[key].split(" & ")[0]
            ytitle = self.feature_names[key].split(" & ")[1]
            return plot_pairwise_heatmap(
                data_dict, title=title, xtitle=xtitle, ytitle=ytitle
            )

        # Handle everything else as invalid
        msg = f"Not supported configuration: {self.explanation_type}, {feature_type}"
        raise Exception(  # pragma: no cover
            msg
        )
