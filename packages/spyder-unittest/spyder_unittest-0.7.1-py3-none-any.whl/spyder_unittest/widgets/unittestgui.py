# -*- coding: utf-8 -*-
#
# Copyright © 2013 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
"""Unit Testing widget."""

# Standard library imports
import ast
import copy
import os.path as osp
import subprocess
import sys

# Third party imports
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QLabel, QMessageBox, QVBoxLayout
from spyder.api.widgets.main_widget import PluginMainWidget
from spyder.config.base import get_conf_path, get_translation
from spyder.utils import icon_manager as ima
from spyder.plugins.variableexplorer.widgets.texteditor import TextEditor

# Local imports
from spyder_unittest.backend.frameworkregistry import FrameworkRegistry
from spyder_unittest.backend.nose2runner import Nose2Runner
from spyder_unittest.backend.pytestrunner import PyTestRunner
from spyder_unittest.backend.runnerbase import Category, TestResult
from spyder_unittest.backend.unittestrunner import UnittestRunner
from spyder_unittest.widgets.configdialog import Config, ask_for_config
from spyder_unittest.widgets.datatree import TestDataModel, TestDataView

# This is needed for testing this module as a stand alone script
try:
    _ = get_translation('spyder_unittest')
except KeyError:
    import gettext
    _ = gettext.gettext

# Supported testing frameworks
FRAMEWORKS = {Nose2Runner, PyTestRunner, UnittestRunner}


class UnitTestWidgetActions:
    RunTests = 'run_tests'
    Config = 'config'
    ShowLog = 'show_log'
    CollapseAll = 'collapse_all'
    ExpandAll = 'expand_all'
    ShowDependencies = 'show_dependencies'


class UnitTestWidgetButtons:
    Start = 'start'


class UnitTestWidgetToolbar:
    LeftStretcher = 'left_stretcher'
    StatusLabel = 'status_label'
    RightStretcher = 'right_stretcher'


class UnitTestWidget(PluginMainWidget):
    """
    Unit testing widget.

    Attributes
    ----------
    config : Config or None
        Configuration for running tests, or `None` if not set.
    default_wdir : str
        Default choice of working directory.
    dependencies : dict or None
        Cached dependencies, as returned by `self.get_versions()`.
    environment_for_dependencies : str or None
        Python interpreter for which `self.dependencies` is valid.
    framework_registry : FrameworkRegistry
        Registry of supported testing frameworks.
    pre_test_hook : function returning bool or None
        If set, contains function to run before running tests; abort the test
        run if hook returns False.
    pythonpath : list of str
        Directories to be added to the Python path when running tests.
    testrunner : TestRunner or None
        Object associated with the current test process, or `None` if no test
        process is running at the moment.

    Signals
    -------
    sig_finished: Emitted when plugin finishes processing tests.
    sig_newconfig(Config): Emitted when test config is changed.
        Argument is new config, which is always valid.
    sig_edit_goto(str, int): Emitted if editor should go to some position.
        Arguments are file name and line number (zero-based).
    """

    CONF_SECTION = 'unittest'
    VERSION = '0.0.1'

    sig_finished = Signal()
    sig_newconfig = Signal(Config)
    sig_edit_goto = Signal(str, int)

    def __init__(self, name, plugin, parent):
        """Unit testing widget."""
        super().__init__(name, plugin, parent)

        self.config = None
        self.default_wdir = None
        self.dependencies = None
        self.environment_for_dependencies = None
        self.output = None
        self.pre_test_hook = None
        self.pythonpath = None
        self.testrunner = None

        self.testdataview = TestDataView(self)
        self.testdatamodel = TestDataModel(self)
        self.testdataview.setModel(self.testdatamodel)
        self.testdataview.sig_edit_goto.connect(self.sig_edit_goto)
        self.testdataview.sig_single_test_run_requested.connect(
            self.run_single_test)
        self.testdatamodel.sig_summary.connect(self.set_status_label)

        self.framework_registry = FrameworkRegistry()
        for runner in FRAMEWORKS:
            self.framework_registry.register(runner)

        layout = QVBoxLayout()
        layout.addWidget(self.testdataview)
        self.setLayout(layout)

    # --- Mandatory PluginMainWidget methods ----------------------------------

    def get_title(self):
        """
        Return the title that will be displayed on dockwidget or window title.
        """
        return _('Unit testing')

    def setup(self):
        """
        Create widget actions, add to menu and other setup requirements.
        """

        # Options menu

        menu = self.get_options_menu()

        config_action = self.create_action(
            UnitTestWidgetActions.Config,
            text=_('Configure ...'),
            icon=self.create_icon('configure'),
            triggered=self.configure)
        self.add_item_to_menu(config_action, menu)

        self.show_log_action = self.create_action(
            UnitTestWidgetActions.ShowLog,
            text=_('Show output'),
            icon=self.create_icon('log'),
            triggered=self.show_log)
        self.add_item_to_menu(self.show_log_action, menu)

        collapse_all_action = self.create_action(
            UnitTestWidgetActions.CollapseAll,
            text=_('Collapse all'),
            icon=self.create_icon('collapse'),
            triggered=self.testdataview.collapseAll)
        self.add_item_to_menu(collapse_all_action, menu)

        expand_all_action = self.create_action(
            UnitTestWidgetActions.ExpandAll,
            text=_('Expand all'),
            icon=self.create_icon('expand'),
            triggered=self.testdataview.expandAll)
        self.add_item_to_menu(expand_all_action, menu)

        show_dependencies_action = self.create_action(
            UnitTestWidgetActions.ShowDependencies,
            text=_('Dependencies'),
            icon=self.create_icon('advanced'),
            triggered=self.show_versions)
        self.add_item_to_menu(show_dependencies_action, menu)

        # Other widgets in the main toolbar

        toolbar = self.get_main_toolbar()

        self.start_button = self.create_toolbutton(UnitTestWidgetButtons.Start)
        self.set_running_state(False)
        self.add_item_to_toolbar(self.start_button, toolbar=toolbar)

        self.add_item_to_toolbar(
            self.create_stretcher(id_=UnitTestWidgetToolbar.LeftStretcher),
            toolbar=toolbar)

        self.status_label = QLabel('')
        self.status_label.ID = UnitTestWidgetToolbar.StatusLabel
        self.add_item_to_toolbar(self.status_label, toolbar=toolbar)

        self.add_item_to_toolbar(
            self.create_stretcher(id_=UnitTestWidgetToolbar.RightStretcher),
            toolbar=toolbar)

    def update_actions(self):
        """
        Update the state of exposed actions.

        Exposed actions are actions created by the self.create_action method.
        """
        pass

    # --- Optional PluginMainWidget methods -----------------------------------

    def get_focus_widget(self):
        """
        Return the test data view as the widget to give focus to.

        Returns
        -------
        QWidget
            QWidget to give focus to.
        """
        return self.testdataview

    # --- UnitTestWidget methods ----------------------------------------------

    @property
    def config(self):
        """Return current test configuration."""
        return self._config

    @config.setter
    def config(self, new_config):
        """Set test configuration and emit sig_newconfig if valid."""
        self._config = new_config
        if self.config_is_valid():
            self.sig_newconfig.emit(new_config)

    def set_config_without_emit(self, new_config):
        """Set test configuration but do not emit any signal."""
        self._config = new_config

    def show_log(self):
        """Show output of testing process."""
        if self.output:
            te = TextEditor(
                self.output,
                title=_("Unit testing output"),
                readonly=True,
                parent=self)
            te.show()
            te.exec_()

    def get_versions(self, use_cached):
        """
        Return versions of frameworks and their plugins.

        If `use_cached` is `True` and `self.environment_for_dependencies`
        equals the Python interpreter set by the user in the Preferences,
        then return the cached information in `self.dependencies`.

        Otherwise, run the `print_versions.py` script in the target
        environment to retrieve the dependencyy information. Store that
        information in `self.dependencies` and return it.

        Parameters
        ----------
        use_cached : bool
            Whether to use the cached information, if possible.

        Returns
        -------
        dict
            Dependency information as returned by `print_versions.py`
        """
        executable = self.get_conf('executable', section='main_interpreter')
        if use_cached and self.environment_for_dependencies == executable:
            return self.dependencies

        script = osp.join(osp.dirname(__file__), osp.pardir, 'backend',
                          'workers', 'print_versions.py')
        process = subprocess.run([executable, script],
                                 capture_output=True, text=True)
        self.dependencies = ast.literal_eval(process.stdout)
        self.environment_for_dependencies = executable
        return self.dependencies

    def show_versions(self):
        """Show versions of frameworks and their plugins"""
        all_info = self.get_versions(use_cached=False)
        versions = [_('Versions of frameworks and their installed plugins:')]
        for name, info in all_info.items():
            if not info['available']:
                versions.append('{}: {}'.format(name, _('not available')))
            else:
                version = f'{name} {info["version"]}'
                plugins = [f'   {name} {version}'
                           for name, version in info['plugins'].items()]
                versions.append('\n'.join([version] + plugins))
        QMessageBox.information(self, _('Dependencies'),
                                '\n\n'.join(versions))

    def configure(self):
        """Configure tests."""
        if self.config:
            oldconfig = self.config
        else:
            oldconfig = Config(wdir=self.default_wdir)
        frameworks = self.framework_registry.frameworks
        versions = self.get_versions(use_cached=True)
        config = ask_for_config(frameworks, oldconfig, versions, parent=self)
        if config:
            self.config = config

    def config_is_valid(self, config=None):
        """
        Return whether configuration for running tests is valid.

        Parameters
        ----------
        config : Config or None
            configuration for unit tests. If None, use `self.config`.
        """
        if config is None:
            config = self.config
        return (config and config.framework
                and config.framework in self.framework_registry.frameworks
                and osp.isdir(config.wdir))

    def maybe_configure_and_start(self):
        """
        Ask for configuration if necessary and then run tests.

        If the current test configuration is not valid (or not set(,
        then ask the user to configure. Then run the tests.
        """
        if not self.config_is_valid():
            self.configure()
        if self.config_is_valid():
            self.run_tests()

    def run_tests(self, config=None, single_test=None):
        """
        Run unit tests.

        First, run `self.pre_test_hook` if it is set, and abort if its return
        value is `False`.

        Then, run the unit tests. If `single_test` is not None, then only run
        that test.

        The process's output is consumed by `read_output()`.
        When the process finishes, the `finish` signal is emitted.

        Parameters
        ----------
        config : Config or None
            configuration for unit tests. If None, use `self.config`.
            In either case, configuration should be valid.
        single_test : str or None
            If None, run all tests; otherwise, it is the name of the only test
            to be run.
        """
        if self.pre_test_hook:
            if self.pre_test_hook() is False:
                return

        if config is None:
            config = self.config
        pythonpath = self.pythonpath
        self.testdatamodel.testresults = []
        self.testdetails = []
        tempfilename = get_conf_path('unittest.results')
        self.testrunner = self.framework_registry.create_runner(
            config.framework, self, tempfilename)
        self.testrunner.sig_finished.connect(self.process_finished)
        self.testrunner.sig_collected.connect(self.tests_collected)
        self.testrunner.sig_collecterror.connect(self.tests_collect_error)
        self.testrunner.sig_starttest.connect(self.tests_started)
        self.testrunner.sig_testresult.connect(self.tests_yield_result)
        self.testrunner.sig_stop.connect(self.tests_stopped)

        cov_path = self.get_conf('current_project_path', default='None',
                                 section='project_explorer')
        # config returns 'None' as a string rather than None
        cov_path = config.wdir if cov_path == 'None' else cov_path
        executable = self.get_conf('executable', section='main_interpreter')
        try:
            self.testrunner.start(
                config, cov_path, executable, pythonpath, single_test)
        except RuntimeError:
            QMessageBox.critical(self,
                                 _("Error"), _("Process failed to start"))
        else:
            self.set_running_state(True)
            self.set_status_label(_('Running tests ...'))

    def set_running_state(self, state):
        """
        Change start/stop button according to whether tests are running.

        If tests are running, then display a stop button, otherwise display
        a start button.

        Parameters
        ----------
        state : bool
            Set to True if tests are running.
        """
        button = self.start_button
        try:
            button.clicked.disconnect()
        except TypeError:  # raised if not connected to any handler
            pass
        if state:
            button.setIcon(ima.icon('stop'))
            button.setText(_('Stop'))
            button.setToolTip(_('Stop current test process'))
            if self.testrunner:
                button.clicked.connect(self.testrunner.stop_if_running)
        else:
            button.setIcon(ima.icon('run'))
            button.setText(_("Run tests"))
            button.setToolTip(_('Run unit tests'))
            button.clicked.connect(
                lambda checked: self.maybe_configure_and_start())

    def process_finished(self, testresults, output, normal_exit):
        """
        Called when unit test process finished.

        This function collects and shows the test results and output.

        Parameters
        ----------
        testresults : list of TestResult
            Test results reported when the test process finished.
        output : str
            Output from the test process.
        normal_exit : bool
            Whether test process exited normally.
        """
        self.output = output
        self.set_running_state(False)
        self.testrunner = None
        self.show_log_action.setEnabled(bool(output))
        self.testdatamodel.add_testresults(testresults)
        self.replace_pending_with_not_run()
        self.sig_finished.emit()
        if not normal_exit:
            self.set_status_label(_('Test process exited abnormally'))

    def replace_pending_with_not_run(self):
        """Change status of pending tests to 'not run''."""
        new_results = []
        for res in self.testdatamodel.testresults:
            if res.category == Category.PENDING:
                new_res = copy.copy(res)
                new_res.category = Category.SKIP
                new_res.status = _('not run')
                new_results.append(new_res)
        if new_results:
            self.testdatamodel.update_testresults(new_results)

    def tests_collected(self, testnames):
        """Called when tests are collected."""
        testresults = [TestResult(Category.PENDING, _('pending'), name)
                       for name in testnames]
        self.testdatamodel.add_testresults(testresults)

    def tests_started(self, testnames):
        """Called when tests are about to be run."""
        testresults = [TestResult(Category.PENDING, _('pending'), name,
                                  message=_('running'))
                       for name in testnames]
        self.testdatamodel.update_testresults(testresults)

    def tests_collect_error(self, testnames_plus_msg):
        """Called when errors are encountered during collection."""
        testresults = [TestResult(Category.FAIL, _('failure'), name,
                                  message=_('collection error'),
                                  extra_text=msg)
                       for name, msg in testnames_plus_msg]
        self.testdatamodel.add_testresults(testresults)

    def tests_yield_result(self, testresults):
        """Called when test results are received."""
        self.testdatamodel.update_testresults(testresults)

    def tests_stopped(self):
        """Called when tests are stopped"""
        self.status_label.setText('')

    def set_status_label(self, msg):
        """
        Set status label to the specified message.

        Arguments
        ---------
        msg: str
        """
        self.status_label.setText('<b>{}</b>'.format(msg))

    def run_single_test(self, test_name: str) -> None:
        """
        Run a single test with the given name.
        """
        self.run_tests(single_test=test_name)


def test():
    """
    Run widget test.

    Show the unittest widgets, configured so that our own tests are run when
    the user clicks "Run tests".
    """
    from spyder.utils.qthelpers import qapplication
    app = qapplication()
    widget = UnitTestWidget(None)

    # set wdir to .../spyder_unittest
    wdir = osp.abspath(osp.join(osp.dirname(__file__), osp.pardir))
    widget.config = Config('pytest', wdir)

    # add wdir's parent to python path, so that `import spyder_unittest` works
    rootdir = osp.abspath(osp.join(wdir, osp.pardir))
    widget.pythonpath = [rootdir]

    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
