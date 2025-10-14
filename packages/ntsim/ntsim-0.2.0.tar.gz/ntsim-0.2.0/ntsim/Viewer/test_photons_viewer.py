def test_photons_viewer(docks,widgets,data,frames,options):
    from ntsim.Viewer.photons_viewer import photons_viewer
    viewer = photons_viewer(frames=frames)
    viewer.set_docks(docks)
    viewer.set_widgets(widgets)
    viewer.set_data(data)
    viewer.configure(options)
    return viewer
