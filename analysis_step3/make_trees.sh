#!/bin/bash
STPOL_ISMC=false analysis_step3/suball.sh out_step3 fileList_Step2/data/*
STPOL_ISMC=true analysis_step3/suball.sh out_step3 fileList_Step2/mc/*
