# Policy buffer and persistent-offset Checkpoint 1

This report is produced from verified solver outputs, not estimates.
Only ideal/assumed-logit software p-bit simulations; no MTJ physical model.

## Stage A: full archived replay and top-16 certification

64,512 main records, exact parity of legacy output and 12 registered contrasts.

| Family | Candidate - FP64 | Mean pp | Lower pp | Upper pp | +0.5 status |
|---|---|---:|---:|---:|---|
| ring | fp5-ref64 | 0.128649 | -0.0018676695623453532 | 0.2724443061845147 | PASS |
| ring | fp6-ref64 | 0.046869 | -0.046795288904021584 | 0.13887414990144004 | PASS |
| ring | int5-ref64 | 0.300659 | 0.14904676937903658 | 0.46628845742041175 | PASS |
| ring | int6-ref64 | 0.089346 | -0.011590761873408476 | 0.20338838674205112 | PASS |
| ring | int7-ref64 | 0.028840 | -0.04944038318559542 | 0.1080624246979219 | PASS |
| ring | int8-ref64 | 0.025180 | -0.014933311457937758 | 0.07697990589001527 | PASS |
| torus | fp5-ref64 | 0.052090 | -0.0693942572300674 | 0.20930884420947876 | PASS |
| torus | fp6-ref64 | 0.063146 | -0.04155269281558581 | 0.16728069909610738 | PASS |
| torus | int5-ref64 | 0.074030 | -0.050282685257632395 | 0.22017939023182403 | PASS |
| torus | int6-ref64 | -0.005544 | -0.10545357336555226 | 0.09654199308248368 | PASS |
| torus | int7-ref64 | -0.014057 | -0.08940499018827129 | 0.06271113924558366 | PASS |
| torus | int8-ref64 | -0.012873 | -0.08850770919641554 | 0.06568040536353259 | PASS |

Original no-buffer certified choices: ring FP5/INT6, k=1; torus FP5/INT5, k=0.
Buffer-policy ladder at tolerances +0.25, +0.5 and +1.0 pp:
{
  "ring": {
    "0.25": {
      "formats": {
        "fp5": "UNRESOLVED",
        "fp6": "PASS",
        "int5": "UNRESOLVED",
        "int6": "PASS",
        "int7": "PASS",
        "int8": "PASS"
      },
      "k_cert": 0,
      "lowest_certified_FP": "fp6",
      "lowest_certified_INT": "int6"
    },
    "0.5": {
      "formats": {
        "fp5": "PASS",
        "fp6": "PASS",
        "int5": "PASS",
        "int6": "PASS",
        "int7": "PASS",
        "int8": "PASS"
      },
      "k_cert": 0,
      "lowest_certified_FP": "fp5",
      "lowest_certified_INT": "int5"
    },
    "1.0": {
      "formats": {
        "fp5": "PASS",
        "fp6": "PASS",
        "int5": "PASS",
        "int6": "PASS",
        "int7": "PASS",
        "int8": "PASS"
      },
      "k_cert": 0,
      "lowest_certified_FP": "fp5",
      "lowest_certified_INT": "int5"
    }
  },
  "torus": {
    "0.25": {
      "formats": {
        "fp5": "PASS",
        "fp6": "PASS",
        "int5": "PASS",
        "int6": "PASS",
        "int7": "PASS",
        "int8": "PASS"
      },
      "k_cert": 0,
      "lowest_certified_FP": "fp5",
      "lowest_certified_INT": "int5"
    },
    "0.5": {
      "formats": {
        "fp5": "PASS",
        "fp6": "PASS",
        "int5": "PASS",
        "int6": "PASS",
        "int7": "PASS",
        "int8": "PASS"
      },
      "k_cert": 0,
      "lowest_certified_FP": "fp5",
      "lowest_certified_INT": "int5"
    },
    "1.0": {
      "formats": {
        "fp5": "PASS",
        "fp6": "PASS",
        "int5": "PASS",
        "int6": "PASS",
        "int7": "PASS",
        "int8": "PASS"
      },
      "k_cert": 0,
      "lowest_certified_FP": "fp5",
      "lowest_certified_INT": "int5"
    }
  }
}

## Stage B: persistent offset validation

27,648 selected-triple and 13,824 specifically registered descriptive-arm runs.

| Family | Registered contrast | Mean pp | Lower pp | Upper pp | +0.5 status |
|---|---|---:|---:|---:|---|
| ring | fp5-int6 | 0.022933 | -0.11929120338327656 | 0.16439488287587473 | PASS |
| ring | fp5-ref64 | 0.293785 | 0.17345964270974906 | 0.44924124918716973 | PASS |
| ring | int6-ref64 | 0.270852 | 0.17947434653937372 | 0.38141206654831716 | PASS |
| torus | fp5-int5 | 0.032094 | -0.07405250572186442 | 0.15119316670247285 | PASS |
| torus | fp5-ref64 | 0.166281 | 0.08010255596321136 | 0.2628645439693186 | PASS |
| torus | int5-ref64 | 0.134188 | 0.029756930957650807 | 0.24210175904959608 | PASS |

See analysis/stage_a_graph_mechanisms.json and stage_b_graph_mechanisms.json
for access, represented selection, earliest-tie, top-16, and ideal-to-offset shifts.
FP6-INT6 under offsets remains descriptive; this does not rerun the weak-tail intervention.
The reused first-block and official-anchor buffer observations are missing.
No gain variation, EDA, hardware or power analyses were performed.
