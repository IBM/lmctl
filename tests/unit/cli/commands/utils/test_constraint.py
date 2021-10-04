import unittest
import click

from ..command_testing import CommandTestCase

from lmctl.cli.commands.utils import constraint, mutually_exclusive

@click.group()
def test_cli():
    pass

def check_B_greater_than_A(a, b, **kwargs):
    if b > a:
        return True, None
    return False, f'"b" value of {b} is not greater than "a" value of {a}'

def check_C_greater_than_B(b, c, **kwargs):
    if c > b:
        return True, None
    return False, f'"c" value of {c} is not greater than "b" value of {b}'

@test_cli.command()
@click.option('-a', type=int)
@click.option('-b', type=int)
@click.option('-c', type=int)
@constraint(check_B_greater_than_A)
def with_constraint(a, b, c):
    pass

def no_reason(**kwargs):
    return False, None

@test_cli.command()
@constraint(no_reason)
def constraint_without_reason():
    pass

@test_cli.command()
@click.option('-a', type=int)
@click.option('-b', type=int)
@click.option('-c', type=int)
@constraint(check_B_greater_than_A)
@constraint(check_C_greater_than_B)
def with_multiple_constraints(a, b, c):
    pass

class TestConstraint(CommandTestCase):

    def test_constraint_pass(self):
        result = self.runner.invoke(with_constraint, ['-a', 1, '-b', 2, '-c', 3])
        self.assert_no_errors(result)

    def test_constraint_fails(self):
        result = self.runner.invoke(with_constraint, ['-a', 1, '-b', 0, '-c', 3])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: with-constraint [OPTIONS]'
        expected_output += '\nTry \'with-constraint --help\' for help.'
        expected_output += '\n\nError: "b" value of 0 is not greater than "a" value of 1'
        self.assert_output(result, expected_output)

    def test_constraint_without_reason_populates_error_with_constraint_func_name(self):
        result = self.runner.invoke(constraint_without_reason, [])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: constraint-without-reason [OPTIONS]'
        expected_output += '\nTry \'constraint-without-reason --help\' for help.'
        expected_output += '\n\nError: N/A (No reason given by constraint: constraint_without_reason)'
        self.assert_output(result, expected_output)

    def test_multiple_constraint_where_one_fails(self):
        result = self.runner.invoke(with_multiple_constraints, ['-a', 1, '-b', 2, '-c', 0])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: with-multiple-constraints [OPTIONS]'
        expected_output += '\nTry \'with-multiple-constraints --help\' for help.'
        expected_output += '\n\nError: "c" value of 0 is not greater than "b" value of 2'
        self.assert_output(result, expected_output)

@test_cli.command()
@click.option('-a', '--alpha', type=int)
@click.option('-b', '--beta', type=int)
@mutually_exclusive(
    ('alpha', '-a, --alpha'),
    ('beta', '-b, --beta')
)
def with_mutual_exclusive_opts(alpha, beta):
    pass

@test_cli.command()
@click.option('--clear-all', is_flag=True, type=bool)
@click.option('--name', type=str)
@mutually_exclusive(
    ('clear_all', '--clear-all'),
    ('name', '--name')
)
def with_mutual_exclusive_bool_opt(clear_all, name):
    pass

@test_cli.command()
@click.option('--clear-all', is_flag=True, type=bool)
@click.option('--name', type=str)
@click.option('--force', is_flag=True, type=bool)
@click.option('--timeout', type=int)
@mutually_exclusive(
    ('clear_all', '--clear-all'),
    ('name', '--name')
)
@mutually_exclusive(
    ('force', '--force'),
    ('timeout', '--timeout')
)
def with_stacked_mutual_exclusive(clear_all, name, force, timeout):
    pass

class TestMutuallyExclusive(CommandTestCase):

    def test_mutex_passes_when_one_opt_set(self):
        result = self.runner.invoke(with_mutual_exclusive_opts, ['-a', 1])
        self.assert_no_errors(result)
        result = self.runner.invoke(with_mutual_exclusive_opts, ['-b', 1])
        self.assert_no_errors(result)

    def test_mutex_fails_when_both_set(self):
        result = self.runner.invoke(with_mutual_exclusive_opts, ['-a', 1, '-b', 2])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: with-mutual-exclusive-opts [OPTIONS]'
        expected_output += '\nTry \'with-mutual-exclusive-opts --help\' for help.'
        expected_output += '\n\nError: Cannot use "-b, --beta" with "-a, --alpha" as they are mutually exclusive'
        self.assert_output(result, expected_output)

    def test_mutex_passes_when_bool_set_to_false(self):
        result = self.runner.invoke(with_mutual_exclusive_bool_opt, ['--name', 'any value'])
        self.assert_no_errors(result)
        
    def test_mutex_fails_when_bool_set_to_true(self):
        result = self.runner.invoke(with_mutual_exclusive_bool_opt, ['--clear-all', '--name', 'any value'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: with-mutual-exclusive-bool-opt [OPTIONS]'
        expected_output += '\nTry \'with-mutual-exclusive-bool-opt --help\' for help.'
        expected_output += '\n\nError: Cannot use "--name" with "--clear-all" as they are mutually exclusive'
        self.assert_output(result, expected_output)

    def test_mutex_passes_when_stacked_checks_ok(self):
        result = self.runner.invoke(with_stacked_mutual_exclusive, ['--name', 'any value', '--force'])
        self.assert_no_errors(result)

    def test_mutex_fails_when_any_stacked_check_fails(self):
        result = self.runner.invoke(with_stacked_mutual_exclusive, ['--name', 'any value', '--timeout', 1, '--force'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: with-stacked-mutual-exclusive [OPTIONS]'
        expected_output += '\nTry \'with-stacked-mutual-exclusive --help\' for help.'
        expected_output += '\n\nError: Cannot use "--timeout" with "--force" as they are mutually exclusive'
        self.assert_output(result, expected_output)
        
        result = self.runner.invoke(with_stacked_mutual_exclusive, ['--name', 'any value', '--clear-all'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: with-stacked-mutual-exclusive [OPTIONS]'
        expected_output += '\nTry \'with-stacked-mutual-exclusive --help\' for help.'
        expected_output += '\n\nError: Cannot use "--name" with "--clear-all" as they are mutually exclusive'
        self.assert_output(result, expected_output)