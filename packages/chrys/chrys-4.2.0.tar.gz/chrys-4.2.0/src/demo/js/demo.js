(function() {
  function setDiscretePalettesVisible(type, visible) {
    jQuery('.nb-discrete-palettes-preview--' + type)[
      visible ? 'hide' : 'show'
    ]();
    jQuery('.nb-discrete-palettes-all--' + type)[visible ? 'show' : 'hide']();
  }

  jQuery('#sequential-discrete, #diverging-discrete')
    .each(function() {
      var $elm = jQuery(this);
      var type = $elm.attr('id').split('-')[0];
      var checked = $elm.is(':checked');
      setDiscretePalettesVisible(type, checked);
    })
    .on('change', function(e) {
      var type = e.target.id.split('-')[0];
      var checked = jQuery(this).is(':checked');
      setDiscretePalettesVisible(type, checked);
    });
})();
