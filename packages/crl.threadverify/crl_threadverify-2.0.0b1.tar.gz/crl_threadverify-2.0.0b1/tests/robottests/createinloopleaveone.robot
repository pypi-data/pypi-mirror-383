# Copyright (C) 2019, Nokia

*** Settings ***

Library   CreateThread.py

*** Test Cases ***


New Threads Leave One
   CreateThread.Create Threads In Loop Leave One    ${iterations}
