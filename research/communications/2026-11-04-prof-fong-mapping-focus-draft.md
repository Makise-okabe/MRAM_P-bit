# WhatsApp draft for Prof Fong — mapping focus

Date: 4 November 2026 (Singapore).
Status: DRAFT — NOT SENT. Prepared for the user to review/copy; no delivery, recipient receipt or approval is implied.
Scope reference: [ADR-0005](../decisions/ADR-0005-one-mapping-study-and-supporting-tools.md).

## Message

Hi Prof Fong, I'd like your advice on consolidating the FYP direction. Of the three options—reliability-aware mapping, failure prediction and Ising—I'd like to focus on mapping as the main method, use the predictor as an evaluation tool, and keep Ising optional.

I've completed an initial workload screen using the frozen MNIST network. It confirms that conventional co-zero grouping can reduce prospective reads, but does not establish an MRAM reliability benefit or novelty.

The proposed contribution is a static row-mapping algorithm that uses calibrated decoded-error structure, including relationships across bit-serial reads, to improve the read-cost versus inference-failure trade-off beyond zero-rate sorting, co-zero grouping, random shuffling and tuned calibration.

The next step is to validate the fresh 256×256 array readout with distributed parasitics and compare practical correction and longer sensing. Only if consequential spatial errors remain would I consider a small split-read controller as an extension of the mapping study.

Would this focused scope and contribution target be appropriate to pursue?
