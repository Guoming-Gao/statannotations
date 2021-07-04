import re
import unittest

import scipy
from packaging import version

import pandas as pd
import seaborn as sns

from statannotations.Annotator import Annotator
from statannotations.utils import DEFAULT


# noinspection DuplicatedCode
class TestAnnotator(unittest.TestCase):
    """Test validation of parameters"""

    def setUp(self):
        self.data = [[1, 2, 3], [2, 5, 7]]
        self.ax = sns.boxplot(data=self.data)
        self.df = pd.DataFrame.from_dict(
            {1: {'x': "a", 'y': 15, 'color': 'blue'},
             2: {'x': "a", 'y': 16, 'color': 'blue'},
             3: {'x': "b", 'y': 17, 'color': 'blue'},
             4: {'x': "b", 'y': 18, 'color': 'blue'},
             5: {'x': "a", 'y': 15, 'color': 'red'},
             6: {'x': "a", 'y': 16, 'color': 'red'},
             7: {'x': "b", 'y': 17, 'color': 'red'},
             8: {'x': "b", 'y': 18, 'color': 'red'}
             }).T

        self.box_pairs_df = [(("a", "blue"), ("b", "blue")),
                             (("a", "blue"), ("a", "red"))]
        self.df.y = self.df.y.astype(float)
        self.params_df = {
            "data": self.df,
            "x": "x",
            "y": "y",
            "hue": "color",
            "order": ["a", "b"],
            "hue_order": ['red', 'blue']}

    def test_init_simple(self):
        self.annot = Annotator(self.ax, [(0, 1)], data=self.data)

    def test_init_df(self):
        self.ax = sns.boxplot(**self.params_df)
        self.annot = Annotator(self.ax, box_pairs=self.box_pairs_df,
                               **self.params_df)

    def test_init_barplot(self):
        ax = sns.barplot(data=self.data)
        self.annot = Annotator(ax, [(0, 1)], plot="barplot", data=self.data)

    def test_test_name_provided(self):
        self.test_init_simple()
        with self.assertRaisesRegex(ValueError, "test"):
            self.annot.apply_test()

    def test_unmatched_x_in_box_pairs_without_hue(self):
        with self.assertRaisesRegex(ValueError, "(specified in `box_pairs`)"):
            self.annot = Annotator(self.ax, [(0, 2)], data=self.data)

    def test_order_in_x(self):
        with self.assertRaisesRegex(ValueError, "(specified in `order`)"):
            self.annot = Annotator(self.ax, [(0, 2)], data=self.data,
                                   order=[0, 1, 2])

    def test_working_hue_orders(self):
        self.annot = Annotator(self.ax, [(("a", "blue"), ("b", "blue"))],
                               data=self.df, x="x", y="y",
                               order=["a", "b"], hue='color',
                               hue_order=['red', 'blue'])

    def test_unmatched_hue_in_hue_order(self):
        with self.assertRaisesRegex(ValueError, "(specified in `hue_order`)"):
            self.annot = Annotator(self.ax, [(("a", "blue"), ("b", "blue"))],
                                   data=self.df, x="x", y="y",
                                   order=["a", "b"], hue='color',
                                   hue_order=['red', 'yellow'])

    def test_unmatched_hue_in_box_pairs(self):
        with self.assertRaisesRegex(ValueError, "(specified in `box_pairs`)"):
            self.annot = Annotator(self.ax, [(("a", "yellow"), ("b", "blue"))],
                                   data=self.df, x="x", y="y",
                                   order=["a", "b"], hue='color',
                                   hue_order=['red', 'blue'])

    def test_unmatched_x_in_box_pairs_with_hue(self):
        with self.assertRaisesRegex(ValueError, "(specified in `box_pairs`)"):
            self.annot = Annotator(self.ax, [(("c", "blue"), ("b", "blue"))],
                                   data=self.df, x="x", y="y",
                                   order=["a", "b"], hue='color',
                                   hue_order=['red', 'blue'])

    def test_location(self):
        self.test_init_simple()
        with self.assertRaisesRegex(ValueError, "argument `loc`"):
            self.annot.configure(loc="somewhere")

    def test_unknown_parameter(self):
        self.test_init_simple()
        with self.assertRaisesRegex(
                ValueError, re.escape("parameter(s) `that`")):
            self.annot.configure(that="this")

    def test_format(self):
        self.test_init_simple()

        with self.assertRaisesRegex(ValueError, "argument `text_format`"):
            self.annot.configure(pvalue_format={'text_format': 'that'})

    def test_apply_comparisons_correction(self):
        self.assertIsNone(Annotator._apply_comparisons_correction(None, []))

    def test_correct_num_custom_annotations(self):
        self.test_init_simple()
        with self.assertRaisesRegex(ValueError, "same length"):
            self.annot.set_custom_annotations(["One", "Two"])

    def test_not_implemented_plot(self):
        with self.assertRaises(NotImplementedError):
            Annotator(self.ax, [(0, 1)], data=self.data, plot="thatplot")

    def test_reconfigure_alpha(self):
        self.test_init_simple()
        with self.assertWarnsRegex(UserWarning, "pvalue_thresholds"):
            self.annot.configure(alpha=0.1)
        self.annot.reset_configuration()
        self.assertEqual(0.05, self.annot.alpha)

    def test_reconfigure_alpha_with_thresholds(self):
        self.test_init_simple()
        self.annot.configure(alpha=0.1,
                             pvalue_format={"pvalue_thresholds": DEFAULT})
        self.annot.reset_configuration()
        self.assertEqual(0.05, self.annot.alpha)

    def test_get_annotation_text_undefined(self):
        self.test_init_simple()
        self.assertIsNone(self.annot.get_annotations_text())

    def test_get_annotation_text_calculated(self):
        self.test_init_simple()
        self.annot.configure(test="Mann-Whitney", verbose=2)
        self.annot.apply_test()
        self.assertEqual(["ns"], self.annot.get_annotations_text())

    def test_get_annotation_text_in_input_order(self):
        self.test_init_df()
        self.annot.configure(test="Mann-Whitney", text_format="simple")
        self.annot.apply_test()

        expected = (['M.W.W. p = 0.25', 'M.W.W. p = 0.67']
                    if version.parse(scipy.__version__) < version.parse("1.7")
                    else ['M.W.W. p = 0.33', 'M.W.W. p = 1.00'])
        self.assertEqual(expected, self.annot.get_annotations_text())

    def test_init_df_inverted(self):
        box_pairs = self.box_pairs_df[::-1]
        self.ax = sns.boxplot(**self.params_df)
        self.annot = Annotator(self.ax, box_pairs=box_pairs, **self.params_df)

    def test_get_annotation_text_in_input_order_inverted(self):
        self.test_init_df_inverted()
        self.annot.configure(test="Mann-Whitney", text_format="simple")
        self.annot.apply_test()

        expected = (['M.W.W. p = 0.67', 'M.W.W. p = 0.25']
                    if version.parse(scipy.__version__) < version.parse("1.7")
                    else ['M.W.W. p = 1.00', 'M.W.W. p = 0.33'])
        self.assertEqual(expected, self.annot.get_annotations_text())

    def test_apply_no_apply_warns(self):
        self.test_init_df_inverted()
        self.annot.configure(test="Mann-Whitney", text_format="simple")
        self.annot.apply_and_annotate()

        self.ax = sns.boxplot(**self.params_df)
        self.annot.new_plot(self.ax, self.box_pairs_df, **self.params_df)
        self.annot.configure(test="Levene", text_format="simple")
        with self.assertWarns(UserWarning):
            self.annot.annotate()

    def test_apply_apply_no_warns(self):
        self.test_init_df_inverted()
        self.annot.configure(test="Mann-Whitney", text_format="simple")
        self.annot.apply_and_annotate()

        self.ax = sns.boxplot(**self.params_df)
        self.annot.new_plot(self.ax, self.box_pairs_df, **self.params_df)
        self.annot.configure(test="Mann-Whitney-gt", text_format="simple")
        self.annot.apply_and_annotate()
