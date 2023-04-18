function emittance = get_emittance

emittance.emit = lcaGet('SR-DI-EMIT-01:EMITTANCE_MEAN');
emittance.coupling = lcaGet('SR-DI-EMIT-01:COUPLING_MEAN');
emittance.espread = lcaGet('SR-DI-EMIT-01:ESPREAD_MEAN');
emittance.hemit = lcaGet('SR-DI-EMIT-01:HEMIT_MEAN');
emittance.veimt = lcaGet('SR-DI-EMIT-01:VEMIT_MEAN');
emittance.herror = lcaGet('SR-DI-EMIT-01:HERROR_MEAN');
emittance.verror = lcaGet('SR-DI-EMIT-01:VERROR_MEAN');