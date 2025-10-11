#if defined(MPI_ABI_VERSION)
#include "compat/mpiabi.h"
#elif defined(I_MPI_NUMVERSION)
#include "compat/impi.h"
#elif defined(MSMPI_VER)
#include "compat/msmpi.h"
#elif defined(MPICH_NAME) && (MPICH_NAME >= 4)
#include "compat/mpich.h"
#elif defined(MPICH_NAME) && (MPICH_NAME == 3)
#include "compat/mpich3.h"
#elif defined(MPICH_NAME) && (MPICH_NAME == 2)
#include "compat/mpich2.h"
#elif defined(MPICH_NAME) && (MPICH_NAME == 1)
#include "compat/mpich1.h"
#elif defined(OPEN_MPI)
#include "compat/openmpi.h"
#endif
#include "compat/mpi-41.h"
#include "compat/mpi-51.h"
