# Copyright (c) 2023 The InterpretML Contributors
# Distributed under the MIT software license

from interpret.glassbox import LogisticRegression
from six import raise_from

from .tutils import assert_valid_explanation, synthetic_classification


def test_import_demo_extension_classes():
    try:
        from interpret.ext.blackbox import ExampleBlackboxExplainer  # noqa
        from interpret.ext.greybox import ExampleGreyboxExplainer  # noqa
        from interpret.ext.glassbox import ExampleGlassboxExplainer  # noqa
        from interpret.ext.data import ExampleDataExplainer  # noqa
        from interpret.ext.perf import ExamplePerfExplainer  # noqa
        from interpret.ext.provider import ExampleVisualizeProvider  # noqa
    except ImportError as import_error:
        raise_from(
            Exception(
                "Failure in demo while trying "
                "to load example explainers through extension_utils",
                import_error,
            ),
            None,
        )


def test_demo_blackbox_explainer():
    from interpret.ext.blackbox import ExampleBlackboxExplainer
    from interpret.ext.data import ExampleDataExplainer
    from interpret.ext.glassbox import ExampleGlassboxExplainer
    from interpret.ext.greybox import ExampleGreyboxExplainer
    from interpret.ext.perf import ExamplePerfExplainer

    data = synthetic_classification()
    blackbox = LogisticRegression()
    blackbox.fit(data["train"]["X"], data["train"]["y"])
    predict_fn = lambda x: blackbox.predict_proba(x)  # noqa: E731

    explainer = ExampleBlackboxExplainer(predict_fn, data["train"]["X"])
    explanation = explainer.explain_local(
        data["test"]["X"].head(), data["test"]["y"].head()
    )
    assert_valid_explanation(explanation)

    explainer = ExampleGreyboxExplainer(blackbox, data["train"]["X"])
    explanation = explainer.explain_local(
        data["test"]["X"].head(), data["test"]["y"].head()
    )
    assert_valid_explanation(explanation)

    explainer = ExampleGlassboxExplainer()
    explainer.fit(data["train"]["X"], data["train"]["y"])
    explainer.predict(data["test"]["X"].head())
    explanation = explainer.explain_local(
        data["test"]["X"].head(), data["test"]["y"].head()
    )
    assert_valid_explanation(explanation)

    explainer = ExampleDataExplainer()
    explanation = explainer.explain_data(
        data["test"]["X"].head(), data["test"]["y"].head()
    )
    assert_valid_explanation(explanation)

    explainer = ExamplePerfExplainer(predict_fn)
    explanation = explainer.explain_perf(
        data["test"]["X"].head(), data["test"]["y"].head()
    )
    assert_valid_explanation(explanation)
