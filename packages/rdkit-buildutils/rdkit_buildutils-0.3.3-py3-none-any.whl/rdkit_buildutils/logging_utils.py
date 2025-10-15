from __future__ import annotations
from contextlib import contextmanager, ExitStack, redirect_stderr, redirect_stdout
from rdkit import RDLogger
import logging, os

@contextmanager
def silence_rdkit(level: str = "CRITICAL"):
    names = ("rdApp.error","rdApp.warning","rdApp.info","rdApp.debug")
    for n in names: RDLogger.DisableLog(n)
    try: yield
    finally:
        for n in names: RDLogger.EnableLog(n)

@contextmanager
def silence_rdkit_all(level: str = "CRITICAL",
                      redirect_stdio: bool = False,
                      *, redir_stderr: bool = True, redir_stdout: bool = False):
    names = [
        "rdkit","rdkit.Chem","rdkit.Chem.MolStandardize",
        "rdkit.Chem.MolStandardize.rdMolStandardize","rdkit.Chem.rdRGroupDecomposition"
    ]
    saved=[]
    with ExitStack() as stack:
        for n in names:
            log=logging.getLogger(n)
            saved.append((log, log.level, log.propagate))
            log.setLevel(logging.CRITICAL); log.propagate=False
        if redirect_stdio or redir_stderr:
            f1=stack.enter_context(open(os.devnull,"w"))
            stack.enter_context(redirect_stderr(f1))
        if redirect_stdio or redir_stdout:
            f2=stack.enter_context(open(os.devnull,"w"))
            stack.enter_context(redirect_stdout(f2))
        try: yield
        finally:
            for log,lvl,prop in saved:
                log.setLevel(lvl); log.propagate=prop
