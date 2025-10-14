
function onReady(fn) {
  if (document.readyState !== 'loading') {
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

onReady(function () {
  function show(id) {
    const el = document.querySelector(`#${id}`)?.closest('.field');
    if (el) el.style.display = '';
  }

  function hide(id) {
    const el = document.querySelector(`#${id}`)?.closest('.field');
    if (el) el.style.display = 'none';
  }

  function groupFields(pxId, choiceId) {
    const pxField = document.querySelector(`#${pxId}`)?.closest('.field');
    const choiceField = document.querySelector(`#${choiceId}`)?.closest('.field');

    if (pxField && choiceField && !pxField.parentNode.classList.contains('inline-field-row')) {
      const wrapper = document.createElement('div');
      wrapper.className = 'inline-field-row';
      pxField.parentNode.insertBefore(wrapper, pxField);
      wrapper.appendChild(pxField);
      wrapper.appendChild(choiceField);
    }
  }

  function updateVisibility() {
    const enablePos = document.querySelector('#form-widgets-enable_widget_icon_position-0');
    const enableSize = document.querySelector('#form-widgets-enable_icon_custom_size-0');

    const rightPx = document.querySelector('#form-widgets-to_the_right_px');
    const right = document.querySelector('#form-widgets-to_the_right');
    const bottomPx = document.querySelector('#form-widgets-to_the_bottom_px');
    const bottom = document.querySelector('#form-widgets-to_the_bottom');
    const sizeValue = document.querySelector('#form-widgets-aioa_size_value');

    if (enablePos && enablePos.checked) {
      show('form-widgets-to_the_right_px');
      show('form-widgets-to_the_right');
      show('form-widgets-to_the_bottom_px');
      show('form-widgets-to_the_bottom');
      hide('form-widgets-aioa_place');
    } else {
      hide('form-widgets-to_the_right_px');
      hide('form-widgets-to_the_right');
      hide('form-widgets-to_the_bottom_px');
      hide('form-widgets-to_the_bottom');
      show('form-widgets-aioa_place');

      // ✅ Reset to defaults
      if (rightPx) rightPx.value = 20;
      if (right) right.value = 'to_the_left';
      if (bottomPx) bottomPx.value = 20;
      if (bottom) bottom.value = 'to_the_bottom';
    }

    if (enableSize && enableSize.checked) {
      show('form-widgets-aioa_size_value');
      hide('form-widgets-aioa_icon_size');
    } else {
      hide('form-widgets-aioa_size_value');
      show('form-widgets-aioa_icon_size');

      // ✅ Reset size to default
      if (sizeValue) sizeValue.value = 50;
    }
  }

  function bindEvents() {
    const enablePos = document.querySelector('#form-widgets-enable_widget_icon_position-0');
    const enableSize = document.querySelector('#form-widgets-enable_icon_custom_size-0');

    if (enablePos) enablePos.addEventListener('change', updateVisibility);
    if (enableSize) enableSize.addEventListener('change', updateVisibility);
  }

  groupFields('form-widgets-to_the_right_px', 'form-widgets-to_the_right');
  groupFields('form-widgets-to_the_bottom_px', 'form-widgets-to_the_bottom');

  updateVisibility();
  bindEvents();
});

// ---------------------- ICON TYPE GRID LOGIC ----------------------

function enhanceIconTypeSelector() {
  const iconField = document.querySelector('#form-widgets-aioa_icon_type');
  if (!iconField) return;

  const values = Array.from(iconField.options).map(opt => opt.value);
  const selectedValue = iconField.value;

  const wrapper = document.createElement('div');
  wrapper.className = 'icon-select-grid';

  values.forEach(val => {
    const div = document.createElement('div');
    div.className = 'icon-select-option';
    if (val === selectedValue) div.classList.add('selected');
    div.dataset.value = val;

    const img = document.createElement('img');
    img.src = `https://www.skynettechnologies.com/sites/default/files/${val}.svg`;
    img.alt = val;

    div.appendChild(img);
    wrapper.appendChild(div);
  });

  iconField.style.display = 'none';
  iconField.parentNode.appendChild(wrapper);

  wrapper.addEventListener('click', function (e) {
    const option = e.target.closest('.icon-select-option');
    if (!option) return;

    const value = option.dataset.value;
    iconField.value = value;
    iconField.dispatchEvent(new Event('change'));

    wrapper.querySelectorAll('.icon-select-option').forEach(el => el.classList.remove('selected'));
    option.classList.add('selected');

    updateSizePreview(value);
  });

  updateSizePreview(selectedValue);
}

const sizeMap = {
  'aioa-big-icon': 75,
  'aioa-medium-icon': 65,
  'aioa-default-icon': 55,
  'aioa-small-icon': 45,
  'aioa-extra-small-icon': 35,
};

function updateSizePreview(selectedIconType) {
  const sizeField = document.querySelector('#form-widgets-aioa_icon_size');
  if (!sizeField) return;

  const values = Array.from(sizeField.options).map(opt => opt.value);
  const wrapperId = 'aioa-size-icon-grid';
  let wrapper = document.getElementById(wrapperId);

  if (wrapper) wrapper.remove();

  wrapper = document.createElement('div');
  wrapper.id = wrapperId;
  wrapper.className = 'icon-select-grid';

  values.forEach(val => {
    const div = document.createElement('div');
    div.className = 'icon-select-option';
    if (val === sizeField.value) div.classList.add('selected');
    div.dataset.value = val;

    const img = document.createElement('img');
    img.src = `https://www.skynettechnologies.com/sites/default/files/${selectedIconType}.svg`;
    img.alt = val;
    img.style.width = `${sizeMap[val]}px`;

    div.appendChild(img);
    wrapper.appendChild(div);
  });

  sizeField.style.display = 'none';
  sizeField.parentNode.appendChild(wrapper);

  wrapper.addEventListener('click', function (e) {
    const option = e.target.closest('.icon-select-option');
    if (!option) return;

    const value = option.dataset.value;
    sizeField.value = value;
    sizeField.dispatchEvent(new Event('change'));

    wrapper.querySelectorAll('.icon-select-option').forEach(el => el.classList.remove('selected'));
    option.classList.add('selected');
  });
}

onReady(() => {
  enhanceIconTypeSelector();
});



