cdef extern from "im-sandbox.h":

    unsigned int QUEUE_SIZE = 256
    unsigned int MAX_EV_LEN = 1024
    unsigned int MAX_NUM_WORKERS = 1024

    struct sb_shm:
        int n_events
        char queue[256][1024] #[QUEUE_SIZE][MAX_EV_LEN]
        int no_more
        char last_ev[1024][1024] #[MAX_NUM_WORKERS][MAX_EV_LEN]
        int pings[1024] #[MAX_NUM_WORKERS]
        int n_processed
        int n_hadcrystals
        int n_crystals
    void create_sandbox(const struct index_args, #*iargs
                       int n_proc, char *prefix, int config_basename, FILE *fh,  Stream *stream,
                       const char *tempdir, int serial_start)

cdef extern from "cell.h":
    ctypedef struct UnitCell #_unitcell UnitCell
    UnitCell *cell_new()
    UnitCell *cell_new_from_cell(const UnitCell *org)
    void cell_free(UnitCell *cell)

cdef extern from "process_image.h":
    struct index_args:
        UnitCell *cell
        int cmfilter;
        int noisefilter
        int median_filter
        int satcorr
        float threshold
        float min_gradient
        float min_snr
        int check_hdf5_snr
        struct detector #*det
        IndexingPrivate #*ipriv
        int peaks             
        float tols[4]
    #struct beam_params #*beam
        char *hdf5_peak_path
        int half_pixel_shift
        float pk_inn
        float pk_mid
        float pk_out
        float ir_inn
        float ir_mid
        float ir_out
        int min_res
        int max_res
        int max_n_peaks
        int min_pix_count
        int max_pix_count
        int local_bg_radius
        int min_peaks
        struct imagefile_field_list #*copyme
        int integrate_saturated
        int use_saturated
        int no_revalidate
        int stream_peaks
        int stream_refls
        int stream_nonhits
        #IntegrationMethod int_meth
        #IntDiag int_diag
        signed int int_diag_h
        signed int int_diag_k
        signed int int_diag_l
        float push_res
        float highres
        float fix_profile_r
        float fix_bandwidth
        float fix_divergence
        int overpredict
        int profile
   # struct taketwo_options #taketwo_opts
   # struct felix_options #felix_opts
    
