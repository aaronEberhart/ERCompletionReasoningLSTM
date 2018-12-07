"""
Completion rules:

C -> D,A -> C                         => A -> D

C1 ^ C2 -> D, A -> C1, A -> C2        => A -> D

C -> ∃R.D,A -> C                      => A -> ∃R.D

∃R.C -> D, A -> ∃R.B, B -> C          => A -> D

R -> S, A -> ∃R.B                     => A -> ∃S.B

R1 o R2 -> R, A -> ∃R1.B, B -> ∃R2.C  => A -> ∃R.C

"""