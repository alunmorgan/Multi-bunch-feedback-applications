function emittance = get_emittance

emittance.emit = get_variable('SR-DI-EMIT-01:EMITTANCE_MEAN');
emittance.coupling = get_variable('SR-DI-EMIT-01:COUPLING_MEAN');
emittance.espread = get_variable('SR-DI-EMIT-01:ESPREAD_MEAN');
emittance.hemit = get_variable('SR-DI-EMIT-01:HEMIT_MEAN');
emittance.veimt = get_variable('SR-DI-EMIT-01:VEMIT_MEAN');
emittance.herror = get_variable('SR-DI-EMIT-01:HERROR_MEAN');
emittance.verror = get_variable('SR-DI-EMIT-01:VERROR_MEAN');