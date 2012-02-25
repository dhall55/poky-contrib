package org.yocto.sdk.remotetools.actions;

import java.io.File;
import java.io.FilenameFilter;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.DirectoryDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.yocto.sdk.remotetools.Activator;
import org.yocto.sdk.remotetools.Messages;
import org.yocto.sdk.remotetools.SWTFactory;

public class BsptoolSettingDialog extends Dialog {
	
	public BsptoolSettingDialog(Shell parent) {
		super(parent);
		// TODO Auto-generated constructor stub
	}

	static protected String title="BspTool";;
	protected boolean showPid=false;
	protected Float time;
	protected Button showPidButton;
	protected Button outLocButton;
	protected Text timeText;
	
	public boolean getShowPid() {
		return showPid;
	}
	
	public Float getTime() {
		return time;
	}
	
	protected void configureShell(Shell newShell) {
		super.configureShell(newShell);
		newShell.setText(title);
	}
	
	protected Control createDialogArea(Composite parent) {
		Composite comp=(Composite)super.createDialogArea(parent);
		GridLayout topLayout = new GridLayout();
		comp.setLayout(topLayout);
		
		/*argument*/
		SWTFactory.createVerticalSpacer(comp, 1);
		createInternal(comp);
		
		return comp;
	}
	
	protected void createInternal(Composite parent)
	{
		Composite projComp = new Composite(parent, SWT.NONE);
		GridLayout projLayout = new GridLayout();
		projLayout.numColumns = 4;
		projLayout.marginHeight = 0;
		projLayout.marginWidth = 0;
		projComp.setLayout(projLayout);
		GridData gd = new GridData(GridData.FILL_HORIZONTAL);
		projComp.setLayoutData(gd);
		
		Label label = new Label(projComp, SWT.NONE);
		label.setText (Messages.BspTool_name);
		gd = new GridData();
		gd.horizontalSpan = 2;
		label.setLayoutData(gd);
		
		Text text = new Text(projComp, SWT.NONE);
		text.setText(""); 
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 2;
		text.setLayoutData(gd);
		
		Label label1 = new Label(projComp, SWT.NONE);
		label1.setText (Messages.BspTool_karch);
		gd = new GridData();
		gd.horizontalSpan = 2;
		label1.setLayoutData(gd);
		
		// gather available kernel arcitectures from file path
		//       scripts/lib/bsp/substrate/target/arch
		// exclude "common"
		
		File dir = new File("./poky-contrib/scripts/lib/bsp/substrate/target/arch");

		String[] children = dir.list();
		if (children == null) {
		    // Either dir does not exist or is not a directory
		} else {
		    for (int i=0; i<children.length; i++) {
		        // Get filename of file or directory
		        String filename = children[i];
		    }
		}

		// Do not return any files that start with 'common'.
		FilenameFilter filter = new FilenameFilter() {
		    public boolean accept(File dir, String name) {
		        return !name.startsWith("common");
		    }
		};
		children = dir.list(filter);

		Combo combo = new Combo (projComp, SWT.NONE);
		combo.setItems (children);
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 2;
		combo.setLayoutData(gd);

		Label label1111 = new Label(projComp, SWT.NONE);
		label1111.setText ("features/debugfs");
		gd = new GridData();
		gd.horizontalSpan = 4;
		label1111.setLayoutData(gd);
		
		Button button = new Button(projComp, SWT.CHECK);
		button.setText("features/drm-emgd");
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 4;
		button.setLayoutData(gd);
		
		Button button1 = new Button(projComp, SWT.CHECK);
		button1.setText("features/ftrace");
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 4;
		button1.setLayoutData(gd);

		Button button11 = new Button(projComp, SWT.CHECK);
		button11.setText("features/ftrace");
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 4;
		button11.setLayoutData(gd);
		
		Button button111 = new Button(projComp, SWT.CHECK);
		button111.setText("features/ericsson-3g");
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 4;
		button111.setLayoutData(gd);
		
		Button button1111 = new Button(projComp, SWT.CHECK);
		button1111.setText("features/intel-e1xxxx");
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 4;
		button1111.setLayoutData(gd);
		
		Button button11111 = new Button(projComp, SWT.CHECK);
		button11111.setText("features/taskstats");
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 4;
		button11111.setLayoutData(gd);
		
		Button button111111 = new Button(projComp, SWT.CHECK);
		button111111.setText("features/yaffs2");
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 4;
		button111111.setLayoutData(gd);
				
		Label label11111 = new Label(projComp, SWT.NONE);
		label11111.setText ("Target Machine Branch");
		gd = new GridData();
		gd.horizontalSpan = 4;
		label11111.setLayoutData(gd);		

		for (int i=0; i<3; i++) {
			Button btnBranch = new Button (projComp, SWT.RADIO);
			if (i == 0) {
				btnBranch.setSelection (true);
				btnBranch.setText("yocto/standard/base");
			} else if (i == 1){
				btnBranch.setText("yocto/standard/common-pc");
			} else {
				btnBranch.setText("yocto/standard/common-pc-64");
			}
				
			gd = new GridData();
			gd.horizontalSpan = 4;
			btnBranch.setLayoutData(gd);
		}
				
		Label lblSMP = new Label(projComp, SWT.NONE);
		lblSMP.setText("SMP support?");
		gd = new GridData();
		gd.horizontalSpan = 4;
		lblSMP.setLayoutData(gd);

		for (int i=0; i<2; i++) {
			Button btnsmp = new Button (projComp, SWT.RADIO);
			if (i == 0) {
				btnsmp.setSelection (true);
				btnsmp.setText("No");
			} else {
				btnsmp.setText("Yes");
			}
			gd = new GridData();
			gd.horizontalSpan = 2;
			btnsmp.setLayoutData(gd);
		}
		
		Label lblX = new Label(projComp, SWT.NONE);
		lblX.setText("Support for X?");
		gd = new GridData();
		gd.horizontalSpan = 4;
		lblX.setLayoutData(gd);

		for (int i=0; i<2; i++) {
			Button btnX = new Button (projComp, SWT.RADIO);
			if (i == 0) {
				btnX.setSelection (true);
				btnX.setText("No");
			} else {
				btnX.setText("Yes");
			}
			gd = new GridData();
			gd.horizontalSpan = 2;
			btnX.setLayoutData(gd);
		}

		Label lblKeyBrd = new Label(projComp, SWT.NONE);
		lblKeyBrd.setText("BSP have a Keyboard?");
		gd = new GridData();
		gd.horizontalSpan = 4;
		lblKeyBrd.setLayoutData(gd);

		for (int i=0; i<2; i++) {
			Button btnKeyBrd = new Button (projComp, SWT.RADIO);
			if (i == 0) {
				btnKeyBrd.setSelection (true);
				btnKeyBrd.setText("No");
			} else {
				btnKeyBrd.setText("Yes");
			}
			gd = new GridData();
			gd.horizontalSpan = 2;
			btnKeyBrd.setLayoutData(gd);
		}

		Label lblTuch = new Label(projComp, SWT.NONE);
		lblTuch.setText("BSP have a touchscreen?");
		gd = new GridData();
		gd.horizontalSpan = 4;
		lblTuch.setLayoutData(gd);

		for (int i=0; i<2; i++) {
			Button btnTuch = new Button (projComp, SWT.RADIO);
			if (i == 0) {
				btnTuch.setSelection (true);
				btnTuch.setText("No");
			} else {
				btnTuch.setText("Yes");
			}
			gd = new GridData();
			gd.horizontalSpan = 2;
			btnTuch.setLayoutData(gd);
		}
		
		Label label111 = new Label(projComp, SWT.NONE);
		label111.setText (Messages.BspTool_out_dir);
		gd = new GridData();
		gd.horizontalSpan = 4;
		label111.setLayoutData(gd);
		
		final Text text1 = new Text(projComp, SWT.NONE);
		text1.setText(""); 
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 3;
		text1.setLayoutData(gd);
		
		outLocButton = SWTFactory.createPushButton(projComp,
				Messages.BspTool_out_dir_btn, null);
		outLocButton.addSelectionListener(new SelectionAdapter() {

			public void widgetSelected(SelectionEvent evt) {
				
				Display display = evt.widget.getDisplay();
				DirectoryDialog dialog = new DirectoryDialog (getShell());
				String platform = SWT.getPlatform();
				dialog.setFilterPath (platform.equals("win32") || platform.equals("wpf") ? "c:\\" : "/");
				String textDir = dialog.open();
				text1.setText(textDir);
				System.out.println ("RESULT=" + dialog.open());
				while (!getShell().isDisposed()) {
					if (!display.readAndDispatch ()) display.sleep ();
				}
				display.dispose ();				
				
				handleOutLocButton();
				//updateLaunchConfigurationDialog();
				updateOutLocText();
			}
		});
		gd = new GridData();
		gd.horizontalSpan = 1;
		outLocButton.setLayoutData(gd);
			
		
	}

	protected void updateOutLocText() {
		// TODO Auto-generated method stub
		
	}

	protected void handleOutLocButton() {
		// TODO something
		
	}
}
